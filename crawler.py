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

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
_logger = logging.getLogger(__name__)

URL = "https://ws.ovh.com/dedicated/r2/ws.dispatcher/getAvailability2"

NOTIFIERS = {
    'email': 'notifiers.email_notifier.EmailNotifier',
    'osx': 'notifiers.osx_notifier.OSXNotifier',
    'popup': 'notifiers.popup_notifier.PopupNotifier',
    'smsapi': 'notifiers.smsapi_notifier.SmsApiNotifier',
}

DATACENTERS = {
    'bhs': 'Beauharnois, Canada (Americas)',
    'gra': 'Gravelines, France',
    'rbx': 'Roubaix, France (Western Europe)',
    'sbg': 'Strasbourg, France (Central Europe)',
    'par': 'Paris, France',
}

STATES = {}
HTTP_ERRORS = []


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
        NOTIFIER.notify(**message)
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
    # for debug only: catch duplicates in json availability
    servers_in_availability = [e['reference'] for e in availability]
    checked = set()
    duplicates = [x for x in servers_in_availability
                  if x in checked and not checked.add(x)]
    if duplicates:
        _logger.info('Servers %s have duplicate availability', duplicates)
        _logger.info('Duplicate entries may result in false positives')
    for item in availability:
        # find server type names of availability item, or continue loop
        server_names = SERVER_TYPES.get(item['reference'])
        if not server_names:
            continue
        # if this server type is not tracked - continue loop
        server_type_match = CONFIG['servers'].intersection(server_names)
        if not server_type_match:
            continue
        server_type = server_type_match.pop()
        # make a flat list of zones where servers of this type are available
        available_zones = [
            e['zone'] for e in item['zones']
            if e['availability'] not in ['unavailable', 'unknown']]
        _logger.debug('%s is available in %s', server_type, available_zones)
        # iterate over all tracked zones and update availability state
        for zone in CONFIG['zones']:
            server_available = zone in available_zones
            state_id = '{name}_available_in_{zone}'.format(
                name=server_type, zone=zone).replace(' ', '_')
            message = {
                'title': "Server {0} available".format(server_type),
                'text': "Server {server_type} is available in {zone}".format(
                    server_type=server_type, zone=zone),
                'url': "http://www.kimsufi.com/fr/index.xml"
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
                "Parsing file %s failed. Check syntax with a JSON validator",
                filename)
            sys.exit(1)
    return result


if __name__ == "__main__":
    # load user config
    CONFIG_NAME = sys.argv[1] if len(sys.argv) == 2 else 'config.json'

    CONFIG = parse_json_file(CONFIG_NAME)
    # Cast CONFIG['servers'] to set
    if isinstance(CONFIG['servers'], list):
        CONFIG['servers'] = set(CONFIG['servers'])
    else:
        _logger.warning("Error in config: CONFIG['servers'] is not a list")
    # load server type mapping
    SERVER_TYPES = parse_json_file('server_types.json')
    # Select notifier, 'email' by default
    if 'notifier' not in CONFIG:

        _logger.warning("No notifier selected in config, 'email' will be used")
        CONFIG['notifier'] = 'email'
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
        _logger.exception("Notifier loading failed,"
                          "check configuration for errors")
        sys.exit(1)

    LOOP = tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(run_crawler, CALLBACK_TIME*1000).start()
    _logger.info("Starting IO loop")

    try:
        LOOP.start()
    except KeyboardInterrupt:
        _logger.info("Terminated by user. Bye.")
        sys.exit(0)
