"""
Sends an email using Gmail's SMTP server.

Args:
    email (str): Recipient's email address.
    subject (str): Subject line of the email.
    message (str): HTML content of the email body.

Raises:
    smtplib.SMTPException: If there is an error sending the email.

Notes:
    - Uses SSL to connect to Gmail's SMTP server.
    - Requires EMAIL and EMAIL_PASSWORD constants for authentication.
    - The email body is sent as HTML.
"""

import smtplib
from email.message import EmailMessage
from utils.consts import EMAIL, EMAIL_PASSWORD


def send_mail(email: str, subject: str, message: str):
    """
    Sends an HTML email using Gmail's SMTP server.
    Args:
        email (str): Recipient's email address.
        subject (str): Subject of the email.
        message (str): HTML content of the email body.
    Raises:
        smtplib.SMTPException: If there is an error sending the email.
    Note:
        Requires EMAIL and EMAIL_PASSWORD to be set as environment variables or constants.
    """

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = email
    msg.add_alternative(message, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL or "", EMAIL_PASSWORD or "")
        smtp.send_message(msg)
        print("Email sent successfully!")
