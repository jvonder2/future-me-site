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
    """
    Send an email via Gmail SMTP.
    - to_email: recipient address
    - subject: email subject line
    - content: either plain-text or HTML, depending on html flag
    - image_path: optional local file path to attach
    - html: if True, send `content` as HTML; otherwise as plain text
    """
    print("Preparing to send email...")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    # Set body
    if html:
        # Fallback plain-text
        msg.set_content("This email contains HTML content, please view in an HTML-capable client.")
        # Add the actual HTML part
        msg.add_alternative(content, subtype="html")
    else:
        msg.set_content(content)

    # Attach image if provided
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
            print(f"🖼 Attached image: {image_path}")

    # Send via Gmail SMTP
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
