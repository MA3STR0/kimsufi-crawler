"""Notifier that sends email messages through SMTP"""

import sys
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
        self.use_starttls = config.get('use_starttls', True)
        self.use_ssl = config.get('use_ssl', False)
        self.fromaddr = config['from_email']
        # smtp user may be different from email
        self.fromuser = config.get('from_user', self.fromaddr)
        self.frompwd = config['from_pwd']
        if sys.version_info[0] == 2:
            self.fromuser = self.fromuser.encode('utf-8')
            self.frompwd = self.frompwd.encode('utf-8')
        self.host = config['from_smtp_host']
        self.port = config.get('from_smtp_port',
                               465 if self.use_ssl else 587)
        self.toaddr = config['to_email']
        self.login_required = self.fromuser and config['from_pwd']
        super(EmailNotifier, self).__init__(config)

    def check_requirements(self):
        """Logs in to SMTP server to check credentials and settings"""
        if self.use_ssl:
            server = smtplib.SMTP_SSL(self.host, self.port)
        else:
            server = smtplib.SMTP(self.host, self.port)
        server.ehlo()
        if self.use_starttls:
            server.starttls()
            server.ehlo()
        try:
            if self.login_required:
                server.login(self.fromuser, self.frompwd)
        except Exception as ex:
            _logger.error("Cannot connect to your SMTP account. "
                          "Correct your config and try again. Error details:")
            _logger.error(ex)
            raise
        _logger.info("SMTP server check passed")

    def notify(self, title, text, url=None):
        """Send email notification using SMTP"""
        msg = MIMEMultipart()
        msg['From'] = self.fromaddr
        msg['To'] = self.toaddr
        msg['Subject'] = title
        body = text if url else text + '\nURL: ' + url
        msg.attach(MIMEText(body, 'plain'))
        if self.use_ssl:
            server = smtplib.SMTP_SSL(self.host, self.port)
        else:
            server = smtplib.SMTP(self.host, self.port)
        server.ehlo()
        if self.use_starttls:
            server.starttls()
            server.ehlo()
        if self.login_required:
          server.login(self.fromuser, self.frompwd)
        text = msg.as_string()
        server.sendmail(self.fromaddr, self.toaddr, text)
