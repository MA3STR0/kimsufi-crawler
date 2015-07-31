"""Notifier that sends messages through Pushover"""

import logging
from chump import Application
from notifiers.base_notifier import Notifier

_logger = logging.getLogger(__name__)


class PushoverNotifier(Notifier):
    """Notifier class to work with Pushover"""

    def __init__(self, config):
        """Override init to make Pushover-settings check"""
        self.application_id = config.get('pushover_application_id', True)
        self.user_id = config.get('pushover_user_id', True)
        super(PushoverNotifier, self).__init__(config)

    def check_requirements(self):
        app = Application(self.application_id)

        try:
            user = app.get_user(self.user_id)
            if not user.is_authenticated:
                raise ValueError("User could not be authenticated")
        except Exception as ex:
            _logger.error("Cannot connect to your Pushover account. "
                          "Correct your config and try again. Error details:")
            _logger.error(ex)
            raise
        _logger.info("Pushover server check passed")

    def notify(self, title, text, url=None):
        app = Application(self.application_id)
        user = app.get_user(self.user_id)

        message = user.send_message(message=text,
                                    title=title,
                                    url=url)


