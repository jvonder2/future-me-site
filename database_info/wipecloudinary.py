#!/usr/bin/env python3
"""
Standalone script to delete all images in a given Cloudinary folder prefix.
Run with:
    python database_info/wipecloudinary.py
"""
import os
import sys
from dotenv import load_dotenv

# Ensure project root is on sys.path so we can import cloudinary_config
script_dir   = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.insert(0, project_root)

# Load environment variables, explicitly pointing to project-root .env
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()  # fallback to default

import cloudinary_config        # loads and configures Cloudinary from CLOUDINARY_URL
from cloudinary import api as cloudinary_api

# Folder prefix used when uploading
PREFIX = "future-me_images"

def clear_images(prefix=PREFIX):
    print(f"🗑️  Clearing all Cloudinary resources with prefix '{prefix}'…")
    try:
        result = cloudinary_api.delete_resources_by_prefix(prefix)
        print("Result:", result)
        return result
    except Exception as e:
        print(f"⚠️  Failed to clear images: {e}")
        print("Make sure CLOUDINARY_URL is set correctly in .env and points to valid credentials.")
        sys.exit(1)

if __name__ == "__main__":
    confirm = input(f"Are you sure you want to permanently delete everything under '{PREFIX}'? (yes/no) ")
    if confirm.strip().lower() == "yes":
        clear_images()
    else:
        print("Aborted. No images were deleted.")
        sys.exit(1)
