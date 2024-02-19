import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64

import requests
from config import password_mail


def send_email(to_mail, code):
    sender = "only.for.creators77@gmail.com"
    template = None
    password =password_mail

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    try:
        msg = MIMEMultipart()
        server.login(sender, password)
        msg["From"] = sender
        msg["To"] = to_mail
        msg.attach(MIMEText(str(code)))
        msg["Subject"] = "Mail confirmation"
        server.sendmail(sender, to_mail, msg.as_string())
        return "The message was sent successfully!"
    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"


def send_email_with_photo(to_mail, code, file_url):
    sender = "only.for.creators77@gmail.com"
    password = password_mail

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    try:
        msg = MIMEMultipart()
        server.login(sender, password)
        msg["From"] = sender
        msg["To"] = to_mail
        msg["Subject"] = "Mail confirmation"
        msg.attach(MIMEText(str(code)))

        response = requests.get(file_url)

        photo_base64 = base64.b64encode(response.content).decode('utf-8')

        image = MIMEImage(base64.b64decode(photo_base64), name='photo.jpg')
        msg.attach(image)

        server.sendmail(sender, to_mail, msg.as_string())
        return "The message was sent successfully!"
    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"

if __name__ == "__main__":
    pass