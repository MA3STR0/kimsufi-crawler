import tornado.ioloop
import tornado.web
import json
import subprocess
from tornado.httpclient import AsyncHTTPClient
from tornado.gen import coroutine
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
_logger = logging.getLogger(__name__)

with open('config.json', 'r') as configfile:
    config=json.loads(configfile.read())

URL = "https://ws.ovh.com/dedicated/r2/ws.dispatcher/getAvailability2"

SERVER_TYPES = {
    '142sk1': 'KS-1',
    '142sk7': 'KS-2',
    '142sk3': 'KS-3',
    '142sk4': 'KS-4',
    '142sk5': 'KS-5',
    '142sk6': 'KS-6',
}

DATACENTERS = {
    'bhs': 'Beauharnois, Canada (Americas)',
    'gra': 'Gravelines, France',
    'rbx': 'Roubaix, France (Western Europe)',
    'sbg': 'Strasbourg, France (Central Europe)',
    'par': 'Paris, France',
}

STATES = {}


def send_mail(title, text, url=False):
    msg = MIMEMultipart()
    fromaddr = config['from_email']
    frompwd = config['from_pwd']
    toaddr = config['to_email']
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = title
    body = text + '\nURL: ' + url
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP(config['from_smtp_host'], config['from_smtp_port'])
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(fromaddr, frompwd)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)


def send_osx_notification(title, text, url=False):
    """Send notification to the user"""
    subprocess.call(['terminal-notifier',
                     '-title', title ,
                     '-message', text,
                     '-open', url
                     ])


def update_state(state, value, message=False):
    """Update state of particular event"""
    # if new value is True and last saved was False
    if state not in STATES:
        STATES[state] = False
    if value is not STATES[state]:
        _logger.info("State change - %s:%s", state, value)
    if value and not STATES[state]:
        send_mail(**message)
    STATES[state] = value


@coroutine
def run_crawler():
    """Run a crawler iteration"""
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(URL)
    response_json = json.loads(response.body.decode('utf-8'))
    availability = response_json['answer']['availability']
    for item in availability:
        if SERVER_TYPES.get(item['reference']) in config['servers']:
            zones = [e['zone'] for e in item['zones']
                     if e['availability'] != 'unavailable']
            if [z for z in config['zones'] if z in zones]:
                server = SERVER_TYPES[item['reference']]
                text = "Server %s is available for in %s" % (server,
                            ', '.join([DATACENTERS[zone] for zone in zones]))
                message = {
                    'title': "Server %s available" % server,
                    'text': text,
                    'url': "http://www.kimsufi.com/fr/index.xml"
                }
                state_id = '%s_available_in_%s' % (server, '+'.join(zones))
                update_state(state_id, True, message)
            else:
                update_state(state_id, False)


if __name__ == "__main__":
    loop = tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(run_crawler, 30000).start()
    loop.start()
