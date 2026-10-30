"""Send mail through Gmail SMTP, logging in with smtp_user / smtp_password."""

import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

import certifi

from config import MAIL_ADDRESS, MAIL_SENDER_NAME, SMTP_PASSWORD, SMTP_USER

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def build_message(to: str, subject: str, text: str, html_body: str, unsubscribe_url: str) -> EmailMessage:
    """A text + HTML mail; List-Unsubscribe lets mail apps show their own unsubscribe button."""
    msg = EmailMessage()
    msg["From"] = formataddr((MAIL_SENDER_NAME, MAIL_ADDRESS))
    msg["To"] = to
    msg["Subject"] = subject
    msg["List-Unsubscribe"] = f"<{unsubscribe_url}>"
    msg.set_content(text)
    msg.add_alternative(html_body, subtype="html")
    return msg


class Mailer:
    """One SMTP connection for a batch of mails: `with Mailer() as m: m.send(msg)`."""

    def __enter__(self):
        if not SMTP_PASSWORD:
            raise RuntimeError("smtp_password is not set (a Gmail app password)")
        # certifi's CA bundle (installed with requests): python.org builds on macOS ship without one
        context = ssl.create_default_context(cafile=certifi.where())
        self.smtp = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=30)
        self.smtp.login(SMTP_USER, SMTP_PASSWORD)
        return self

    def send(self, msg: EmailMessage):
        self.smtp.send_message(msg)

    def __exit__(self, *exc):
        self.smtp.quit()
