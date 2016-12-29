"""Notifier that sends messages through Pushbullet"""

import logging
from pushbullet import Pushbullet
from notifiers.base_notifier import Notifier

_logger = logging.getLogger(__name__)


class PushbulletNotifier(Notifier):
    """Notifier class to work with Pushbullet"""

    def __init__(self, config):
        """Override init to check settings"""
        self.pushbullet_apikey = config['pushbullet_apikey']
        super(PushbulletNotifier, self).__init__(config)

    def check_requirements(self):
        try:
            pb = Pushbullet(self.pushbullet_apikey)
        except Exception as ex:
            _logger.error("Cannot connect to your Pushbullet account. "
                          "Correct your config and try again. Error details:")
            _logger.error(ex)
            raise
        _logger.info("Pushbullet server check passed")

    def notify(self, title, text, url=None):
        pb = Pushbullet(self.pushbullet_apikey)
        push = pb.push_link(text, url)