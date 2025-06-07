# test_cloudinary.py
import cloudinary
from cloudinary.uploader import upload

print("Cloud:", cloudinary.config().cloud_name)
print("Key:  ", bool(cloudinary.config().api_key), "Secret:", bool(cloudinary.config().api_secret))

# Try uploading a small local image
resp = upload("path/to/a/local/image.jpg", upload_preset="unsigned_future_me")
print("Upload response:", resp)
