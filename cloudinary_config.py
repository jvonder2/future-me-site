# cloudinary_config.py
import os
import cloudinary

# If a single CLOUDINARY_URL is set, cloudinary.config() will pick it up automatically
cloudinary.config(secure=True)

# Optional sanity‐check:
if not cloudinary.config().api_secret:
    raise RuntimeError("Missing CLOUDINARY_URL or API secret")
