#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Crawler that sends notifications as soon as servers
on Kimsufi/OVH become available for purchase"""

import json
import sys
import os
import re
import logging
import importlib
import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPError
from tornado.gen import coroutine
# Python 3 imports
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
_logger = logging.getLogger(__name__)
CURRENT_PATH = os.path.dirname(__file__)


def parse_json_file(filename):
    """open file and parse its content as json"""
    with open(filename, 'r') as jsonfile:
        content = jsonfile.read()
        try:
            result = json.loads(content)
        except ValueError:
            _logger.error(
                "Parsing file %s failed. Check syntax with a JSON validator:"
                "\nhttp://jsonlint.com/?json=%s", filename, quote(content))
            sys.exit(1)
    return result


class Crawler(object):
    """Crawler responsible for fetching availability and monitoring states"""

    def __init__(self, state_change_callback):
        # set properties
        self.state_change_callback = state_change_callback

        # load mappings
        self.SERVER_TYPES = parse_json_file(
            os.path.join(CURRENT_PATH, 'mapping/server_types.json'))
        self.REGIONS = parse_json_file(
            os.path.join(CURRENT_PATH, 'mapping/regions.json'))

        # set private vars
        self.API_URL = ("https://ws.ovh.com/dedicated/r2/ws.dispatcher"
                        "/getAvailability2")
        self.STATES = {}
        self.HTTP_ERRORS = []
        self.interval = 8   # seconds between interations
        self.periodic_cb = None
        self.ioloop = None
        self.http_client = AsyncHTTPClient()

    def update_state(self, state, value, message=None):
        """Update state of particular event"""
        # if state is new, init it as False
        if state not in self.STATES:
            self.STATES[state] = False
        # compare new value to old value
        if value is not self.STATES[state]:
            _logger.debug("State change - %s: %s", state, value)
        # notify, if state changed from False to True
        if value and not self.STATES[state]:
            self.state_change_callback(state, message)
        # save the new value
        self.STATES[state] = value

    def resume_periodic_cb(self):
        _logger.info("Crawler resumed")
        self.periodic_cb.start()

    @coroutine
    def run(self):
        """Run a crawler iteration"""
        progress()
        try:
            # request OVH availability API asynchronously
            resp = yield self.http_client.fetch(self.API_URL,
                                                request_timeout=REQUEST_TIMEOUT)
        except HTTPError as ex:
            # Internal Server Error
            self.HTTP_ERRORS.append(ex)
            if len(self.HTTP_ERRORS) > 5:
                if all([e.code == 500 for e in self.HTTP_ERRORS]):
                    _logger.error("Server continiously returns error 500 and "
                                  "may be down, check the status manually: %s",
                                  self.API_URL)
                else:
                    _logger.error("Too many HTTP Errors: %s", self.HTTP_ERRORS)
                self.HTTP_ERRORS = []
            return
        except Exception as gex:
            # Also catch other errors.
            _logger.error("Socket Error: %s", str(gex))
            return
        if self.HTTP_ERRORS:
            del self.HTTP_ERRORS[:]
        response_json = json.loads(resp.body.decode('utf-8'))
        if response_json.get('error'):
            if response_json['error']['status'] == 451:
                match = re.search(r'will be replenished in (\d+) seconds.',
                                  response_json['error'].get('message', ''))
                timeout = int(match.group(1)) if match else 28800
                _logger.error("Rate-limit error, have to pause for %d seconds",
                              timeout)
                self.periodic_cb.stop()
                self.ioloop.call_later(timeout, self.resume_periodic_cb)
                self.interval *= 2
                _logger.info("New request interval: %d seconds", self.interval)
                return
        if not response_json or not response_json['answer']:
            _logger.error("No answer from API: %s", response_json)
            return
        availability = response_json['answer']['availability']
        for item in availability:
            # get server type of availability item
            server_type = self.SERVER_TYPES.get(item['reference'])
            # return if this server type is not in mapping
            if not server_type:
                continue
            # make a flat list of zones where servers of this type are available
            available_zones = set([
                e['zone'] for e in item['zones']
                if e['availability'] not in ['unavailable', 'unknown']])
            _logger.debug('%s is available in %s', server_type, available_zones)
            # iterate over all regions and update availability states
            for region, places in self.REGIONS.items():
                server_available = bool(available_zones.intersection(places))
                state_id = '%s_available_in_%s' % (server_type.lower(),
                                                   region.lower())
                message = {
                    'title': "{0} is available".format(server_type),
                    'text': "Server {server} is available in {region}".format(
                        server=server_type, region=region.capitalize()),
                    'url': "http://www.kimsufi.com/en/index.xml"
                }
                if 'sys' in item['reference'] or 'bk' in item['reference']:
                    message['url'] = 'http://www.soyoustart.com/de/essential-server/'
                self.update_state(state_id, server_available, message)


def bell():
    sys.stdout.write('\a')
    sys.stdout.flush()


def progress():
    sys.stdout.write('.')
    sys.stdout.flush()


if __name__ == "__main__":
    # load user config
    _CONFIG = parse_json_file(os.path.join(CURRENT_PATH, 'config.json'))

    # init notifier
    _NOTIFIERS = {
        'pushover': 'notifiers.pushover_notifier.PushoverNotifier',
        'email': 'notifiers.email_notifier.EmailNotifier',
        'osx': 'notifiers.osx_notifier.OSXNotifier',
        'popup': 'notifiers.popup_notifier.PopupNotifier',
        'popup_pywin': 'notifiers.popup_pywin_notifier.PopupPywinNotifier',
        'smsapi': 'notifiers.smsapi_notifier.SmsApiNotifier',
        'xmpp': 'notifiers.xmpp_notifier.XMPPNotifier',
        'pushbullet': 'notifiers.pushbullet_notifier.PushbulletNotifier',
        'file': 'notifiers.file_notifier.FileNotifier',
        'freemobile': 'notifiers.freemobile_notifier.FreemobileNotifier',
        'telegram': 'notifiers.telegram_notifier.TelegramNotifier',
    }
    # Select notifier, 'email' by default
    if 'notifier' not in _CONFIG:
        _logger.warning("No notifier selected in config, 'email' will be used")
        _CONFIG['notifier'] = 'email'
    # Instantiate notifier class dynamically
    try:
        _NOTIFIER_PATH = _NOTIFIERS[_CONFIG['notifier']]
        _NOTIFIER_FILE, _NOTIFIER_CLASSNAME = _NOTIFIER_PATH.rsplit('.', 1)
        _NOTIFIER_MODULE = importlib.import_module(_NOTIFIER_FILE)
        NOTIFIER = getattr(_NOTIFIER_MODULE, _NOTIFIER_CLASSNAME)(_CONFIG)
    except Exception as ex:
        _logger.exception("Notifier loading failed, check config for errors")
        sys.exit(1)

    # prepare states tracked by the user
    TRACKED_STATES = []
    for server in _CONFIG['servers']:
        TRACKED_STATES.append(
            '%s_available_in_%s' % (server.lower(), _CONFIG['region'].lower()))
    _logger.info('Tracking states: %s', TRACKED_STATES)

    # define state-change callback to notify the user
    def state_changed(state, message=None):
        """Trigger notifications"""
        message = message or {}
        if state in TRACKED_STATES:
            _logger.info("Will notify: %s", state)
            NOTIFIER.notify(**message)
            bell()

    # Check and set request timeout
    REQUEST_TIMEOUT = _CONFIG.get('request_timeout', 30)

    # Init the crawler
    crawler = Crawler(state_change_callback=state_changed)
    crawler.periodic_cb = tornado.ioloop.PeriodicCallback(
        crawler.run, crawler.interval * 1000)
    crawler.periodic_cb.start()

    # start the IOloop
    _logger.info("Starting main loop")
    crawler.ioloop = tornado.ioloop.IOLoop.instance()
    try:
        crawler.ioloop.start()
    except KeyboardInterrupt:
        _logger.info("Terminated by user. Bye.")
        sys.exit(0)
