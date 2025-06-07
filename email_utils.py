from dotenv import load_dotenv
load_dotenv()

import os
import requests
import mimetypes
from email.message import EmailMessage
import smtplib

EMAIL_ADDRESS  = os.getenv("GMAIL_USER")
EMAIL_PASSWORD = os.getenv("GMAIL_PASS")

def send_email(to_email, subject, content, images: list[str] = None, html: bool = False):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = EMAIL_ADDRESS
    msg["To"]      = to_email

    # 1) Plain-text version: exactly what the user typed
    msg.set_content(content)

    # 2) HTML alternative: translate \n into <br> so line-breaks show up
    html_body = content.replace("\n", "<br>")
    msg.add_alternative(html_body, subtype="html")

    # 3) Attach images as real attachments
    for img in images or []:
        fname = os.path.basename(img)
        # Download if it's a URL
        if img.startswith("http"):
            resp = requests.get(img)
            resp.raise_for_status()
            data = resp.content
        else:
            with open(img, "rb") as f:
                data = f.read()

        mime_type, _ = mimetypes.guess_type(fname)
        if mime_type:
            maintype, subtype = mime_type.split("/", 1)
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=fname)

    # 4) Send via SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
