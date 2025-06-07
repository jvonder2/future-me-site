# email_utils.py

from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage
import mimetypes

load_dotenv()

EMAIL_ADDRESS = os.getenv("GMAIL_USER")
EMAIL_PASSWORD = os.getenv("GMAIL_PASS")

def send_email(to_email, subject, content, image_path=None, html=False):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    if html:
        msg.set_content("This message contains HTML. Please view in an HTML client.")
        msg.add_alternative(content, subtype="html")
    else:
        msg.set_content(content)

    if image_path and os.path.exists(image_path):
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type:
            maintype, subtype = mime_type.split("/", 1)
            with open(image_path, "rb") as img:
                msg.add_attachment(
                    img.read(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=os.path.basename(image_path)
                )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)