# cloudinary_config.py

import os
import cloudinary

CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL")
if not CLOUDINARY_URL:
    raise RuntimeError("CLOUDINARY_URL environment variable is not set.")

# This parses CLOUDINARY_URL for you
cloudinary.config(cloudinary_url=CLOUDINARY_URL, secure=True)
