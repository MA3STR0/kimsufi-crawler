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
from tornado.gen import coroutine

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
_logger = logging.getLogger(__name__)

with open('config.json', 'r') as configfile:
    config = json.loads(configfile.read())

URL = "https://ws.ovh.com/dedicated/r2/ws.dispatcher/getAvailability2"

NOTIFIERS = {
    'email': 'notifiers.email_notifier.EmailNotifier',
    'osx': 'notifiers.osx_notifier.OSXNotifier',
    'popup': 'notifiers.popup_notifier.PopupNotifier'
}

SERVER_TYPES = {
    '142sk1': 'KS-1',
    '142sk7': 'KS-2',
    '142sk3': 'KS-3',
    '142sk4': 'KS-4',
    '142sk5': 'KS-5A',
    '142sk8': 'KS-5B',
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


def update_state(state, value, message=False):
    """Update state of particular event"""
    # if new value is True and last saved was False
    if state not in STATES:
        STATES[state] = False
    if value is not STATES[state]:
        _logger.info("State change - %s: %s", state, value)
    if value and not STATES[state]:
        notifier.notify(**message)
    STATES[state] = value


@coroutine
def run_crawler():
    """Run a crawler iteration"""
    http_client = AsyncHTTPClient()
    # request OVH availablility API asynchronously
    response = yield http_client.fetch(URL)
    response_json = json.loads(response.body.decode('utf-8'))
    if not response_json or not response_json['answer']:
        return
    availability = response_json['answer']['availability']
    for item in availability:
        # look for servers of required types in OVH availability list
        if SERVER_TYPES.get(item['reference']) in config['servers']:
            # make a flat list of zones where servers are available
            available_zones = [e['zone'] for e in item['zones']
                               if e['availability'] != 'unavailable']
            # iterate over all tacked zones and set availability states
            for zone in config['zones']:
                server = SERVER_TYPES[item['reference']]
                state_id = '%s_available_in_%s' % (server, zone)
                # update state for each tracked zone
                text = "Server %s is available in %s" % (server, zone)
                message = {
                    'title': "Server %s available" % server,
                    'text': text,
                    'url': "http://www.kimsufi.com/fr/index.xml"
                }
                update_state(state_id, zone in available_zones, message)


if __name__ == "__main__":
    # Select notifier, 'email' by default
    if 'notifier' not in config:
        _logger.warning("No notifier selected in config, 'email' will be used")
        config['notifier'] = 'email'
    # Instantiate notifier class dynamically
    try:
        n_path = NOTIFIERS[config['notifier']]
        n_file, n_classname = n_path.rsplit('.', 1)
        n_module = importlib.import_module(n_file)
        notifier = getattr(n_module, n_classname)(config)
    except:
        _logger.exception("Notifier loading failed, check configuration for errors")
        sys.exit(1)

    loop = tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(run_crawler, 30000).start()
    _logger.info("Starting IO loop")

    try:
        loop.start()
    except KeyboardInterrupt:
        _logger.info("Terminated by user. Bye.")
        sys.exit(0)
