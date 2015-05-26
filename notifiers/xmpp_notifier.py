"""Notifier that sends messages through XMPP/JABBER"""

import logging

from notifiers.base_notifier import Notifier
import xmpp


_logger = logging.getLogger(__name__)


class XMPPNotifier(Notifier):
    """Notifier class to work with xmpp"""

    def __init__(self, config):
        """Override init to check settings"""
        self.xmpp_jid = config['xmpp_jid']
        self.xmpp_password = config['xmpp_password']
        self.xmpp_recipient = config['xmpp_recipient']
        self.xmpp_send_test = config.get('xmpp_send_test', False)
        super(XMPPNotifier, self).__init__(config)

    def check_requirements(self):
        """Log in to xmpp server and check credentials"""
        jid = xmpp.protocol.JID(self.xmpp_jid)
        try:
            cl = xmpp.Client(jid.getDomain(),debug=[])
            if not cl.connect():
                raise Exception("Connect failed.")

            if not cl.auth(jid.getNode(), self.xmpp_password, resource=jid.getResource()):
                raise Exception("Authentication failed.")

            if self.xmpp_send_test:
                if not cl.send(xmpp.protocol.Message(self.xmpp_recipient, 'Kimsufi Crawler: Initial Test Message')):
                    raise Exception("Failed to send message to %s" % (self.xmpp_recipient, ))
                _logger.info("XMPP sent: [%s] %s" % (self.xmpp_recipient, 'Kimsufi Crawler: Initial Test Message'))

        except Exception as ex:
            _logger.error("Cannot connect/auth to XMPP Server. "
                          "Correct your config and try again. Error details:")
            _logger.error(ex)
            raise
        _logger.info("XMPP connected.")

    def notify(self, title, text, url=False):
        """Send XMPP notification"""
        body = text + ' - ' + url
        jid = xmpp.protocol.JID(self.xmpp_jid)
        cl = xmpp.Client(jid.getDomain(),debug=[])
        if not cl.connect():
            raise Exception("Connect failed.")

        if not cl.auth(jid.getNode(), self.xmpp_password, resource=jid.getResource()):
            raise Exception("Authentication failed.")

        if not cl.send(xmpp.protocol.Message(self.xmpp_recipient, body)):
            raise Exception("Failed to send message to %s" % (self.xmpp_recipient, ))
        _logger.info("XMPP sent: [%s] %s" % (self.xmpp_recipient, body))
