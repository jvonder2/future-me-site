from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from checkdb import get_pending_messages, mark_as_sent
from email_utils import send_email
import tempfile
import requests
import os

def check_and_send():
    now = datetime.now()
    print(f"🕒 Checking for due messages at {now.isoformat()}…")
    pending = get_pending_messages()
    print(f"   → {len(pending)} pending message(s) found")

    for doc in pending:
        msg_id     = str(doc["_id"])
        recipient  = doc["email"]
        body_text  = doc["body"]
        image_urls = doc.get("image_urls", [])

        print(f"   • Preparing to send {msg_id} to {recipient} with {len(image_urls)} attachment(s)")

        # Download attachments to temp files
        local_paths = []
        for url in image_urls:
            try:
                r = requests.get(url)
                r.raise_for_status()
                suffix = os.path.splitext(url)[1] or ".jpg"
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp.write(r.content)
                    local_paths.append(tmp.name)
            except Exception as e:
                print(f"     ⚠️  Failed to download {url}: {e}")

        # Send email with attachments
        send_email(
            to_email=recipient,
            subject="Your Future-Me Message",
            content=body_text,
            images=local_paths,
            html=False
        )
        print(f"   ✔️  Sent {msg_id}")

        # Clean up temp files
        for path in local_paths:
            try:
                os.remove(path)
            except:
                pass

        mark_as_sent(msg_id)

def start_scheduler():
    print("⏰ Scheduler starting…")
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send, 'interval', minutes=1)
    scheduler.start()
    print("✅ Scheduler started – will check every minute for due messages")
