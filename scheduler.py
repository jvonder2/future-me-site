from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import sqlite3
from email_utils import send_email

def send_due_emails():
    print("🕒 Checking for due messages at", datetime.now())

    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute("SELECT * FROM messages WHERE send_date <= ? AND sent = 0", (now,))
        due = c.fetchall()

        print(f"🔍 Found {len(due)} message(s) due")

        for row in due:
            print(f"📨 Sending to {row[1]} with message: {row[2]}")
            send_email(row[1], row[2])
            c.execute("UPDATE messages SET sent = 1 WHERE id = ?", (row[0],))
        conn.commit()

def start_scheduler():
    print("⏰ Scheduler starting...")

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_due_emails, 'interval', seconds=10)  # reduced for test speed
    scheduler.start()
    print("✅ Scheduler started")
