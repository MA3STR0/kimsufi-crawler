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

SERVER_TYPES = {
    '150sk10': 'KS-1',
    '150sk20': 'KS-2a',
    '150sk21': 'KS-2b',
    '150sk22': 'KS-2c',
    '150sk30': 'KS-3',
    '150sk31': 'KS-3',
    '150sk40': 'KS-4',
    '150sk41': 'KS-4',
    '150sk42': 'KS-4',
    '150sk50': 'KS-5',
    '150sk60': 'KS-6',
    '141game1': 'GAME-1',
    '141game2': 'GAME-2',
    '141game3': 'GAME-3',

}

DATACENTERS = {
    'bhs': 'Beauharnois, Canada (Americas)',
    'gra': 'Gravelines, France',
    'rbx': 'Roubaix, France (Western Europe)',
    'sbg': 'Strasbourg, France (Central Europe)',
    'par': 'Paris, France',
}

STATES = {}


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
        _logger.error("HTTP Error: {0}".format(ex))
        return
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
        # get server type of availability item
        server_type = SERVER_TYPES.get(item['reference'])
        # return if this server type is not tracked
        if server_type not in CONFIG['servers']:
            return
        # make a flat list of zones where servers of this type are available
        available_zones = [
            e['zone'] for e in item['zones']
            if e['availability'] not in ['unavailable', 'unknown']]
        _logger.debug('%s is available in %s', server_type, available_zones)
        # iterate over all tracked zones and update availability state
        for zone in CONFIG['zones']:
            server_available = zone in available_zones
            state_id = '%s_available_in_%s' % (server_type, zone)
            message = {
                'title': "Server {0} available".format(server_type),
                'text': "Server {server_type} is available in {zone}".format(
                    server_type=server_type, zone=zone),
                'url': "http://www.kimsufi.com/fr/index.xml"
            }
            update_state(state_id, server_available, message)


if __name__ == "__main__":
    CONFIG_NAME = sys.argv[1] if len(sys.argv) == 2 else 'config.json'
    with open(CONFIG_NAME, 'r') as configfile:
        try:
            CONFIG = json.loads(configfile.read())
        except ValueError:
            _logger.error("Parsing JSON settings in config.json has failed. "
                          "Check syntax with a validator (i.e. jsonlint.com)")
            sys.exit(1)

    # Select notifier, 'email' by default
    if 'notifier' not in CONFIG:
        _logger.warning("No notifier selected in config, 'email' will be used")
        CONFIG['notifier'] = 'email'
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
    tornado.ioloop.PeriodicCallback(run_crawler, 15000).start()
    _logger.info("Starting IO loop")

    try:
        LOOP.start()
    except KeyboardInterrupt:
        _logger.info("Terminated by user. Bye.")
        sys.exit(0)
