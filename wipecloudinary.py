# wipe_cloudinary.py

from dotenv import load_dotenv
import os
import cloudinary
from cloudinary.api import delete_resources_by_prefix
import urllib.parse


# 1) Load .env so CLOUDINARY_URL is in os.environ
load_dotenv()

cloudinary_url = os.environ.get("CLOUDINARY_URL")
if not cloudinary_url:
    raise RuntimeError(
        "CLOUDINARY_URL not set. "
        "Please add CLOUDINARY_URL=cloudinary://<API_KEY>:<API_SECRET>@<CLOUD_NAME> "
        "to your .env"
    )

# 2) Parse it: cloudinary://API_KEY:API_SECRET@CLOUD_NAME
parsed = urllib.parse.urlparse(cloudinary_url)
# parsed.netloc == "API_KEY:API_SECRET@CLOUD_NAME"
creds, _, cloud_name = parsed.netloc.rpartition("@")
api_key, _, api_secret = creds.partition(":")

# 3) Configure the SDK explicitly
cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret,
    secure=True
)
cfg = cloudinary.config()
print("Using Cloudinary config:", cfg.cloud_name, cfg.api_key, cfg.api_secret)

# 4) Delete everything under the "future-me_images" folder
result = delete_resources_by_prefix("future-me_images")

# 5) Report what was deleted
print("✅ Cloudinary wiped. Deleted resources:")
for public_id, status in result.get("deleted", {}).items():
    print(f" • {public_id}: {status}")
