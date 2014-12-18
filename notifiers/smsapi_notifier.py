"""Notifier that sends messages through smsapi.pl, Polish SMS service"""

import logging

from notifiers.base_notifier import Notifier
from smsapi import SmsApi


_logger = logging.getLogger(__name__)


class SmsApiNotifier(Notifier):
    """Notifier class to work with email"""

    def __init__(self, config):
        """Override init to check settings"""
        self.smsapi_username = config['smsapi_username']
        self.smsapi_password = config['smsapi_password']
        self.smsapi_recipient = config['smsapi_recipient']

        super(SmsApiNotifier, self).__init__(config)

    def check_requirements(self):
        """Log in to smsapi and check credentials and settings"""
        sms = SmsApi(self.smsapi_username, self.smsapi_password)
        try:
            total_points = sms.get_points()['points']
        except Exception as ex:
            _logger.error("Cannot connect to your SMSAPI account. "
                          "Correct your config and try again. Error details:")
            _logger.error(ex)
            raise
        _logger.info("SMSAPI connected. You have %s points." % total_points)

    def notify(self, title, text, url=False):
        """Send sms notification using smsapi.pl"""
        body = text + ' - ' + url
        sms = SmsApi(self.smsapi_username, self.smsapi_password)
        sms.send_sms(body, recipient=self.smsapi_recipient)
        _logger.info("SMSAPI sent: [%s] %s" % (self.smsapi_recipient, body))
