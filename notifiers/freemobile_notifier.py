"""Notifier that sends sms to freemobile client using FM notifications API"""

import logging
import webbrowser
from notifiers.base_notifier import Notifier

_logger = logging.getLogger(__name__)


class FreemobileNotifier(Notifier):
    """Notifier class for freemobile sms"""

    def __init__(self, config):
        self.username = config.get('freemobile_username', '')
        self.password = config.get('freemobile_key', '')

        super(FreemobileNotifier, self).__init__(config)

    def check_requirements(self):
        """Check requests library is installed"""
        try:
            __import__('requests')
        except ImportError:
            raise Warning(
                "requests Python library is required for freemobile notifications. ")

    def notify(self, title, text, url=False):
        """"""
        import requests

        requests.get("https://smsapi.free-mobile.fr/sendmsg?user={user}&pass={key}&msg={msg}"
            .format(user=self.username, key=self.password, msg='Kimsufi: '+text))
