"""Notifier that opens a popup window"""

import logging
import webbrowser
from notifiers.base_notifier import Notifier

_logger = logging.getLogger(__name__)


class PopupPywinNotifier(Notifier):
    """Notifier class for popup windows, a windows specific version"""

    def check_requirements(self):
        """Check platform and notifier command"""
        lib_name = "win32api"
        try:
            __import__(lib_name)
        except ImportError:
            raise Warning(
                "{} Python library is required".format(lib_name))

    def notify(self, title, text, url=False):
        """Open popup notification window with easygui"""
        import win32api
        # 0x00001000 -- Value represents MB_SYSTEMMODAL
        # This is to allow for the messagebox to sit over every window
        # Something that is not possible using easygui (as far as I'm aware)
        if win32api.MessageBox(0, text, title, 0x00001000) == 1:
            webbrowser.open_new_tab(url)
