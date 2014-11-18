"""Generic notifier, to be subclassed"""

import logging
_logger = logging.getLogger(__name__)


class Notifier(object):
    """Abstract class for notifiers"""
    def __init__(self, config):
        """Save config and run system check"""
        self.config = config
        self.check_requirements()
        _logger.info("Notification system check passed")

    def check_requirements(self):
        """Abstract method to check requirements, config, dependencies etc"""
        raise NotImplementedError

    def notify(self, title, text, url=False):
        """Abstract method for notification sending"""
        raise NotImplementedError
