# checkdb.py

from db import messages_coll
from datetime import datetime, timezone
from bson.objectid import ObjectId

def save_message(email: str, body: str, send_date: datetime, image_url: str = None) -> str:
    doc = {
        "email": email,
        "body": body,
        "send_date": send_date,
        "sent": False,
        "created_at": datetime.now(timezone.utc),
        "image_url": image_url
    }
    result = messages_coll.insert_one(doc)
    return str(result.inserted_id)

def get_pending_messages() -> list:
    now = datetime.now(timezone.utc)
    cursor = messages_coll.find({
        "send_date": {"$lte": now},
        "sent": False
    })
    return list(cursor)

def mark_as_sent(message_id: str) -> int:
    result = messages_coll.update_one(
        { "_id": ObjectId(message_id) },
        { "$set": { "sent": True, "sent_at": datetime.now(timezone.utc) } }
    )
    return result.modified_count