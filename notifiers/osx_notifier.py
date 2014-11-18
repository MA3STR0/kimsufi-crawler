"""Notifier that sends Mac OSX desktop notifications"""

import logging
import subprocess
import platform
import os
from notifiers.base_notifier import Notifier

_logger = logging.getLogger(__name__)


class OSXNotifier(Notifier):
    """Notifier class for OSX desktop notifications"""

    def check_requirements(self):
        """Check platform and notifier command"""
        if platform.system() != 'Darwin':
            raise Warning("You are not running Mac OS X, "
                          "this notification plugin will not work.")
        try:
            subprocess.call(['terminal-notifier', '--version'],
                            stdout=open(os.devnull, 'w'),
                            stderr=subprocess.STDOUT)
        except OSError:
            raise Warning(
                "terminal-notifier library is required for OSX notifications. "
                "You can install it by running in terminal:\n"
                "sudo gem install terminal-notifier")

    def notify(self, title, text, url=False):
        """Send Mac-OS-X notification using terminal-notifier"""
        subprocess.call(['terminal-notifier',
                         '-title', title,
                         '-message', text,
                         '-open', url])
