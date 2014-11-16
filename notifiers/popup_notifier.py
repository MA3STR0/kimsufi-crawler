"""Notifier that sends Mac OSX desktop notifications"""

import logging
import webbrowser
from notifiers.base_notifier import Notifier

_logger = logging.getLogger(__name__)


class PopupNotifier(Notifier):
    """Notifier class for popup windows"""

    def check_requirements(self):
        """Check platform and notifier command"""
        try:
            __import__('easygui')
        except ImportError:
            raise Warning(
                "easygui Python library is required for popup notifications. "
                "You can install it by running in terminal:\n"
                "sudo easy_install easygui")

    def notify(self, title, text, url=False):
        """Open popup notification window with easygui"""
        import easygui
        if easygui.ccbox(text, title, ["Open web page", "Ignore"]):
            webbrowser.open_new_tab(url)
