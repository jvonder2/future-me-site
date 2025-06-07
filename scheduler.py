# scheduler.py

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from checkdb import get_pending_messages, mark_as_sent
from email_utils import send_email

def check_and_send():
    print(f"🕒 Checking for due messages at {datetime.now()}…")
    for doc in get_pending_messages():
        msg_id = str(doc["_id"])
        recipient = doc["email"]
        body_text = doc["body"]
        image_url = doc.get("image_url")

        if image_url:
            html_body = f"{body_text}<br><br><img src='{image_url}' alt='User image'/>"
            send_email(recipient, "Your Future-Me Message", html_body, html=True)
        else:
            send_email(recipient, "Your Future-Me Message", body_text)

        mark_as_sent(msg_id)

def start_scheduler():
    print("⏰ Scheduler starting…")
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send, 'interval', minutes=1)
    scheduler.start()
    print("✅ Scheduler started")