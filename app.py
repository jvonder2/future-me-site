'''
Additions that I want to make to this code:
1. add in more console debugging messages such as when the scheduler starts, when a message is sent, what messages need to be sent, etc.
2. be able to clear my cloudinary images via a REST API call
3. allow the users to upload more than one image
4. allow the user to see immediately after they send their message what they sent in an email format
5. make it so that the images sent are attachments not inline images
6. add a default header to the email such as "Hello future me!"
'''

from dotenv import load_dotenv
load_dotenv()

import os
import tempfile
import requests
from flask import Flask, request, render_template, jsonify
from datetime import datetime
from checkdb import save_message
from scheduler import start_scheduler
import cloudinary_config
from cloudinary import config as cloudinary_config_lib

app = Flask(
    __name__,
    template_folder="frontend",
    static_folder="frontend",
    static_url_path=""
)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-if-missing")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api/send-later", methods=["POST"])
def api_send_later():
    # 1) Read form fields
    email = request.form.get("email", "").strip()
    body = request.form.get("body", "").strip()
    send_date_str = request.form.get("send_date", "").strip()
    if not (email and body and send_date_str):
        return jsonify({"error": "Email, message, and send date are required"}), 400

    # 2) Parse the ISO-UTC string from the browser
    try:
        if send_date_str.endswith("Z"):  # Convert trailing 'Z' to '+00:00'
            send_date_str = send_date_str[:-1] + "+00:00"
        send_date = datetime.fromisoformat(send_date_str)
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    # 3) Optional image upload via direct REST call to Cloudinary
    image_url = None
    image_file = request.files.get("image")
    if image_file and image_file.filename:
        suffix = os.path.splitext(image_file.filename)[1]
        # Save to a temp file for upload
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            image_file.save(tmp.name)
            tmp_path = tmp.name

        try:
            # Construct unsigned upload endpoint
            cfg = cloudinary_config_lib()  # Uses CLOUDINARY_URL from environment
            url = f"https://api.cloudinary.com/v1_1/{cfg.cloud_name}/image/upload"

            with open(tmp_path, "rb") as f:
                files = {"file": f}
                data = {
                    "upload_preset": "unsigned_future_me",
                    "folder": "future-me_images",
                }
                resp = requests.post(url, data=data, files=files)
                resp.raise_for_status()
                upload_res = resp.json()
                image_url = upload_res.get("secure_url")
        finally:
            os.remove(tmp_path)

    # 4) Save to MongoDB
    doc_id = save_message(
        email=email,
        body=body,
        send_date=send_date,
        image_url=image_url
    )

    return jsonify({"status": "scheduled", "id": doc_id}), 200

# Start the scheduler once
start_scheduler()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
