"""Notifier that sends a message to the specified chat through Telegram"""

import logging
from notifiers.base_notifier import Notifier
import telegram
from telegram.error import TelegramError

_logger = logging.getLogger(__name__)


class TelegramNotifier(Notifier):
    """Notifier class for Telegram"""

    def __init__(self, config):
        self.chat_id = config.get('telegram_chat_id')
        token = config.get('telegram_token')
        self.bot = telegram.Bot(token=token)
        super().__init__(config)

    def check_requirements(self):
        try:
            self.bot.get_me()
            self.bot.send_message(chat_id=self.chat_id, text="Kimsufi Crawler started")
        except TelegramError as te:
            _logger.error("Telegram validation failed: {error}".format(error=te.message))
            raise

    def notify(self, title, text, url=None):
        try:
            self.bot.send_message(chat_id=self.chat_id, text=text)
        except TelegramError as te:
            _logger.error("Something went wrong sending the message to Telegram:")
            _logger.error(te)
