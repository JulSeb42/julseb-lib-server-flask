import smtplib
from email.message import EmailMessage
from utils.consts import EMAIL, EMAIL_PASSWORD, SITE_DATA


def send_mail(email: str, subject: str, message: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = email
    msg.add_alternative(message, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL or "", EMAIL_PASSWORD or "")
        smtp.send_message(msg)
        print("Email sent successfully!")
