from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage
import mimetypes

load_dotenv()

EMAIL_ADDRESS = os.getenv("GMAIL_USER")
EMAIL_PASSWORD = os.getenv("GMAIL_PASS")

def send_email(to_email, content, image_path=None):
    print("Preparing to send via Gmail SMTP...")

    msg = EmailMessage()
    msg["Subject"] = "A message from your past self"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(content)

    # Attach image if provided
    if image_path and os.path.exists(image_path):
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type:
            maintype, subtype = mime_type.split("/")
            with open(image_path, "rb") as img:
                msg.add_attachment(
                    img.read(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=os.path.basename(image_path)
                )
            print(f"🖼 Attached image: {image_path}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
