# app.py

from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, request, render_template, jsonify
from datetime import datetime

from checkdb import save_message
from scheduler import start_scheduler

import cloudinary_config  # reads CLOUDINARY_URL
from cloudinary.uploader import upload as cloudinary_upload

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

    # 2) Parse the ISO-UTC string the browser sent
    try:
        # Convert trailing 'Z' → '+00:00' so fromisoformat accepts it
        if send_date_str.endswith("Z"):
            send_date_str = send_date_str[:-1] + "+00:00"
        send_date = datetime.fromisoformat(send_date_str)
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    # 3) Handle optional unsigned upload to Cloudinary
    image_file = request.files.get("image")
    image_url = None
    if image_file and image_file.filename:
        upload_res = cloudinary_upload(
            image_file,
            upload_preset="unsigned_future_me",  # your unsigned preset in Cloudinary
            unsigned=True,
            folder="future-me_images"
        )
        image_url = upload_res.get("secure_url")

    # 4) Save to MongoDB
    doc_id = save_message(
        email=email,
        body=body,
        send_date=send_date,
        image_url=image_url
    )

    return jsonify({"status": "scheduled", "id": doc_id}), 200


# Start the scheduler exactly once
start_scheduler()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))