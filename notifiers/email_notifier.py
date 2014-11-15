"""Notifier that sends email messages through SMTP"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from notifiers.base_notifier import Notifier

_logger = logging.getLogger(__name__)


class EmailNotifier(Notifier):
    """Notifier class to work with email"""

    def __init__(self, config):
        """Override init to make SMTP-settings check"""
        self.fromaddr = config['from_email']
        # smtp user may be different from email
        self.fromuser = config.get('from_user', self.fromaddr)
        self.frompwd = config['from_pwd']
        self.host = config['from_smtp_host']
        self.port = config['from_smtp_port']
        self.toaddr = config['to_email']
        super(EmailNotifier, self).__init__(config)

    def check_requirements(self):
        """Logs in to SMTP server to check credentials and settings"""
        server = smtplib.SMTP(self.host, self.port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        try:
            server.login(self.fromuser, self.frompwd)
        except Exception as ex:
            _logger.error("Cannot connect to your SMTP account. "
                          "Correct your config and try again. Error details:")
            _logger.error(ex)
            raise
        _logger.info("SMTP server check passed")

    def notify(self, title, text, url=False):
        """Send email notification using SMTP"""
        msg = MIMEMultipart()
        msg['From'] = self.fromaddr
        msg['To'] = self.toaddr
        msg['Subject'] = title
        body = text + '\nURL: ' + url
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(self.host, self.port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self.fromuser, self.frompwd)
        text = msg.as_string()
        server.sendmail(self.fromaddr, self.toaddr, text)
