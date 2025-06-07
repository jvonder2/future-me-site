# db.py

import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGODB_URI", "").strip()
if not MONGO_URI:
    raise RuntimeError("MONGODB_URI environment variable is not set.")

client = MongoClient(MONGO_URI)
db = client.get_default_database()
messages_coll = db["messages"]
