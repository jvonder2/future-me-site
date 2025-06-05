from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage

load_dotenv()

EMAIL_ADDRESS = os.getenv("GMAIL_USER")
EMAIL_PASSWORD = os.getenv("GMAIL_PASS")

def send_email(to_email, content):
    print("📤 Preparing to send via Gmail SMTP...")

    msg = EmailMessage()
    msg["Subject"] = "A message from your past self ✉️"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(content)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
