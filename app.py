# app.py

# 1) Load .env first so MONGODB_URI, CLOUDINARY_*, SECRET_KEY are in os.environ
from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from datetime import datetime

from checkdb import save_message
from apscheduler.schedulers.background import BackgroundScheduler

# Cloudinary config (reads CLOUDINARY_CLOUD_NAME, etc.)
import cloudinary_config
from cloudinary.uploader import upload as cloudinary_upload

# 2) Create Flask app: use frontend/ for both templates and static files
app = Flask(
    __name__,
    template_folder="frontend",
    static_folder="frontend",
    static_url_path=""
)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-if-missing")


@app.route("/", methods=["GET"])
def index():
    """Render the HTML form."""
    return render_template("index.html")


@app.route("/api/send-later", methods=["POST"])
def api_send_later():
    """
    Accepts multipart/form-data:
      - email, body, send_date in request.form
      - optional file in request.files['image']
    Uploads image (if any) UNSIGNED via your unsigned preset,
    saves doc in Mongo, returns JSON.
    """
    from datetime import datetime
    from flask import request, jsonify
    from cloudinary.uploader import upload as cloudinary_upload
    from checkdb import save_message

    # 1) Read text fields
    email         = request.form.get("email", "").strip()
    body          = request.form.get("body", "").strip()
    send_date_str = request.form.get("send_date", "").strip()

    # 2) Validate
    if not (email and body and send_date_str):
        return jsonify({"error": "Email, message, and send date are required"}), 400

    try:
        send_date = datetime.fromisoformat(send_date_str)
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    # 3) Handle optional file (UNSIGNED upload)
    image_file = request.files.get("image")
    image_url = None
    if image_file and image_file.filename:
        upload_res = cloudinary_upload(
            image_file,
            upload_preset="unsigned_future_me",  # your unsigned preset name
            unsigned=True,                       # <- turns off signature
            folder="future-me_images"            # allowed in unsigned
        )
        image_url = upload_res.get("secure_url")

    # 4) Save everything to Mongo
    doc_id = save_message(
        email=email,
        body=body,
        send_date=send_date,
        image_url=image_url
    )

    # 5) Return success
    return jsonify({"status": "scheduled", "id": doc_id}), 200


# 3) Start the background scheduler
from scheduler import start_scheduler
start_scheduler()


if __name__ == "__main__":
    # Local dev only; in production Render/Werkzeug handles this
    app.run(host="127.0.0.1", port=5000)
