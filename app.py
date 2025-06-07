# app.py

from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, request, render_template, jsonify
from datetime import datetime, timezone

from checkdb import save_message
from scheduler import start_scheduler

import cloudinary_config
from cloudinary.uploader import upload as cloudinary_upload

app = Flask(
    __name__,
    template_folder="frontend",
    static_folder="frontend",
    static_url_path=""
)
app.secret_key = os.environ.get("SECRET_KEY", "dev")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api/send-later", methods=["POST"])
def api_send_later():
    """
    Accepts multipart/form-data:
      - email, body, send_date in request.form
      - optional file in request.files['image']
    Parses the user's local datetime, converts it to UTC-aware,
    uploads the image unsigned, saves to Mongo, and returns JSON.
    """
    from datetime import datetime, timezone
    import tzlocal
    from flask import request, jsonify
    from cloudinary.uploader import upload as cloudinary_upload
    from checkdb import save_message

    # 1) Read text fields
    email         = request.form.get("email", "").strip()
    body          = request.form.get("body", "").strip()
    send_date_str = request.form.get("send_date", "").strip()

    # 2) Basic validation
    if not (email and body and send_date_str):
        return jsonify({"error": "Email, message, and send date are required"}), 400

    # 3) Parse and convert to UTC
    try:
        # parse naive local datetime from the HTML datetime-local input
        naive = datetime.fromisoformat(send_date_str)
        # get system local timezone
        local_tz = tzlocal.get_localzone()
        # attach local tzinfo
        local_dt = naive.replace(tzinfo=local_tz)
        # convert to UTC
        send_date = local_dt.astimezone(timezone.utc)
        # strip tzinfo if your DB expects naive UTC
        # send_date = send_date.replace(tzinfo=None)
    except Exception:
        return jsonify({"error": "Invalid date format"}), 400

    # 4) Handle optional image upload (unsigned)
    image_file = request.files.get("image")
    image_url = None
    if image_file and image_file.filename:
        upload_res = cloudinary_upload(
            image_file,
            upload_preset="unsigned_future_me",
            unsigned=True,
            folder="future-me_images"
        )
        image_url = upload_res.get("secure_url")

    # 5) Save to MongoDB
    doc_id = save_message(
        email=email,
        body=body,
        send_date=send_date,
        image_url=image_url
    )

    # 6) Return success
    return jsonify({"status": "scheduled", "id": doc_id}), 200

# start the scheduler once
start_scheduler()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
