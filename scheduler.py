from checkdb import get_pending_messages, mark_as_sent
from email_utils import send_email
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

def check_and_send():
    """
    Find all messages in Mongo whose send_date ≤ now and sent == False,
    send them (with image if present), and mark them as sent.
    """
    pending = get_pending_messages()
    for doc in pending:
        msg_id    = str(doc["_id"])
        recipient = doc["email"]
        body_text = doc["body"]
        image_url = doc.get("image_url")  # may be None

        if image_url:
            # Embed the image URL into an HTML email body
            html_body = f"{body_text}<br><br><img src='{image_url}' alt='User‐uploaded image' />"
            send_email(recipient, "Your Future-Me Message", html_body, html=True)
        else:
            # Send plain-text if no image
            send_email(recipient, "Your Future-Me Message", body_text)

        # Mark as sent in MongoDB
        mark_as_sent(msg_id)

def start_scheduler():
    """
    Start APScheduler to run check_and_send() every minute.
    Call this function once (e.g. at application startup).
    """
    print(f"⏰ Scheduler starting at {datetime.now()}...")
    scheduler = BackgroundScheduler()
    # Run check_and_send() every 60 seconds
    scheduler.add_job(check_and_send, trigger="interval", minutes=1)
    scheduler.start()
    print("✅ Scheduler started")

# If you’d rather have the scheduler start automatically when you import this file,
# uncomment the next line:
# start_scheduler()
