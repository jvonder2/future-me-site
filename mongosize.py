# mongo_usage.py
from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()
client = MongoClient(os.environ["MONGODB_URI"])
db = client.get_default_database()

stats = db.command("dbstats")
print(f"dataSize:    {stats['dataSize']/(1024**2):.2f} MB")
print(f"storageSize: {stats['storageSize']/(1024**2):.2f} MB")
print(f"indexSize:   {stats['indexSize']/(1024**2):.2f} MB")