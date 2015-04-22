#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Crawler that sends notifications as soon as servers
on Kimsufi/OVH become available for purchase"""

import json
import sys
import logging
import importlib
import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPError
from tornado.gen import coroutine
from urllib import quote

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
_logger = logging.getLogger(__name__)

URL = "https://ws.ovh.com/dedicated/r2/ws.dispatcher/getAvailability2"

STATES = {}
HTTP_ERRORS = []
TRACKED_STATES = []
NOTIFIERS = {
    'email': 'notifiers.email_notifier.EmailNotifier',
    'osx': 'notifiers.osx_notifier.OSXNotifier',
    'popup': 'notifiers.popup_notifier.PopupNotifier',
    'smsapi': 'notifiers.smsapi_notifier.SmsApiNotifier',
}


def notify_subscribers(state, message=False):
    """Trigger notifications for subscribers of event"""
    if state in TRACKED_STATES:
        NOTIFIER.notify(**message)


def update_state(state, value, message=False):
    """Update state of particular event"""
    # if state is new, init it as False
    if state not in STATES:
        STATES[state] = False
    # compare new value to old value
    if value is not STATES[state]:
        _logger.info("State change - %s: %s", state, value)
    # notify, if state changed from False to True
    if value and not STATES[state]:
        notify_subscribers(state, message)
    # save the new value
    STATES[state] = value


@coroutine
def run_crawler():
    """Run a crawler iteration"""
    http_client = AsyncHTTPClient()
    # request OVH availablility API asynchronously
    try:
        response = yield http_client.fetch(URL)
    except HTTPError as ex:
        # Internal Server Error
        HTTP_ERRORS.append(ex)
        if len(HTTP_ERRORS) > 3:
            _logger.error("Too many HTTP Errors: %s", HTTP_ERRORS)
        return
    if HTTP_ERRORS:
        del HTTP_ERRORS[:]
    response_json = json.loads(response.body.decode('utf-8'))
    if not response_json or not response_json['answer']:
        return
    availability = response_json['answer']['availability']
    for item in availability:
        # get server type of availability item
        server_type = SERVER_TYPES.get(item['reference'])
        # return if this server type is not tracked
        if server_type not in CONFIG['servers']:
            continue
        # make a flat list of zones where servers of this type are available
        available_zones = set([
            e['zone'] for e in item['zones']
            if e['availability'] not in ['unavailable', 'unknown']])
        _logger.debug('%s is available in %s', server_type, available_zones)
        # iterate over all locations and update availability states
        for location, datacenters in REGIONS.items():
            server_available = bool(available_zones.intersection(datacenters))
            state_id = '%s_available_in_%s' % (server_type, location)
            message = {
                'title': "{0} is available".format(server_type),
                'text': "Server {server} is available in {loc}".format(
                    server=server_type, loc=location),
                'url': "http://www.kimsufi.com/en/index.xml"
            }
            update_state(state_id, server_available, message)


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


if __name__ == "__main__":
    # load user config
    CONFIG = parse_json_file('config.json')
    # load mappings
    SERVER_TYPES = parse_json_file('mapping/server_types.json')
    REGIONS = parse_json_file('mapping/regions.json')
    # Select notifier, 'email' by default
    if 'notifier' not in CONFIG:
        _logger.warning("No notifier selected in config, 'email' will be used")
        CONFIG['notifier'] = 'email'

    # prepare states tracked by the user
    for track_server_type in CONFIG['servers']:
        TRACKED_STATES.append(
            '%s_available_in_%s' % (track_server_type, CONFIG['region']))

    # Check and set periodic callback time
    CALLBACK_TIME = CONFIG.get('crawler_interval', 10)
    if CALLBACK_TIME < 7.2:
        _logger.warning("Selected crawler interval of %s seconds is less than "
                        "7.2, client may be rate-limited by OVH", CALLBACK_TIME)
    # Instantiate notifier class dynamically
    try:
        NOTIFIER_PATH = NOTIFIERS[CONFIG['notifier']]
        NOTIFIER_FILE, NOTIFIER_CLASSNAME = NOTIFIER_PATH.rsplit('.', 1)
        NOTIFIER_MODULE = importlib.import_module(NOTIFIER_FILE)
        NOTIFIER = getattr(NOTIFIER_MODULE, NOTIFIER_CLASSNAME)(CONFIG)
    except Exception as ex:
        _logger.exception("Notifier loading failed, check config for errors")
        sys.exit(1)

    LOOP = tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(run_crawler, CALLBACK_TIME*1000).start()
    _logger.info("Starting IO loop")

    try:
        LOOP.start()
    except KeyboardInterrupt:
        _logger.info("Terminated by user. Bye.")
        sys.exit(0)
