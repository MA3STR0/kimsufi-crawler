"""Notifier that append text to a given file"""
"""
This notifier should be used with think kind of browser plugin:
https://chrome.google.com/webstore/detail/distill-web-monitor/inlikjemeeknofckkjolnjbpehgadgge
(doesn't seem to work directly on KS website)
You can set up this plugin to be notified with a sound, desktop notifs...
You can run it somewhere and check the availibility from any web browser!
"""

import os
import datetime
import logging
from notifiers.base_notifier import Notifier

_logger = logging.getLogger(__name__)

class FileNotifier(Notifier):
    """Notifier class to work with file"""

    def __init__(self, config):
        self.file_path = config.get('file_path')
        super(FileNotifier, self).__init__(config)

    def check_requirements(self):
        """Check if file exist"""
        if not os.path.isfile(self.file_path):
            _logger.error("File not found")
            _logger.error(ex)
            raise
        _logger.info("File notifier check passed")

    def notify(self, title, text, url=None):
        """Update html file"""
        with open(self.file_path, "a") as file:
            ts = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
            file.write('<br/>AVAILABLE! - %s' % ts)