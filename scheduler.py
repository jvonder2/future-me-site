import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from email_utils import send_email
import os

# Define the folder where uploads live
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

def check_and_send_due_messages():
    print(f"🕒 Checking for due messages at {datetime.now()}")
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, email, message, image_path "
            "FROM messages "
            "WHERE sent = 0 AND send_date <= datetime('now')"
        )
        due_messages = c.fetchall()

        print(f"🔍 Found {len(due_messages)} message(s) due")

        for msg_id, email, content, image_filename in due_messages:
            print(f"📨 Sending to {email} with message: {content}")

            # If image_filename is not None, build full path under uploads/
            attachment_path = None
            if image_filename:
                candidate = os.path.join(UPLOAD_FOLDER, image_filename)
                if os.path.exists(candidate):
                    attachment_path = candidate
                else:
                    print(f"⚠️  Attachment not found: {candidate}")

            send_email(email, content, attachment_path)

            c.execute("UPDATE messages SET sent = 1 WHERE id = ?", (msg_id,))

        conn.commit()

def start_scheduler():
    print("⏰ Scheduler starting...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send_due_messages, 'interval', seconds=10)
    scheduler.start()
    print("✅ Scheduler started")
