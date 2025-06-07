from pymongo import MongoClient
import os

# Load your MONGODB_URI however you like; here we assume dotenv:
from dotenv import load_dotenv
load_dotenv()

client = MongoClient(os.environ["MONGODB_URI"])
db = client.get_default_database()

# 1) To delete only the messages collection:
db.messages.drop()

# 2) Or, to delete all documents but keep the collection:
# db.messages.delete_many({})

print("MongoDB wiped ✅")
