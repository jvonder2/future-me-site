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

@app.route("/api/preview", methods=["POST"])
def api_preview():
    # 1) Read form fields
    email         = request.form.get("email", "").strip()
    body          = request.form.get("body", "").strip()
    send_date_str = request.form.get("send_date", "").strip()
    raw_local     = request.form.get("raw_local", "").strip()
    if not (email and body and send_date_str and raw_local):
        return jsonify({"error": "Email, message, and send date are required"}), 400

    # 2) Parse date (for future scheduling -- still use UTC internally)
    try:
        if send_date_str.endswith("Z"):
            send_date_str = send_date_str[:-1] + "+00:00"
        send_date = datetime.fromisoformat(send_date_str)
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    # 3) Handle multi-image upload
    image_urls = []
    for image_file in request.files.getlist("images"):
        if not image_file or not image_file.filename:
            continue
        suffix = os.path.splitext(image_file.filename)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            image_file.save(tmp.name)
            tmp_path = tmp.name
        try:
            cfg = cloudinary_config_lib()
            url = f"https://api.cloudinary.com/v1_1/{cfg.cloud_name}/image/upload"
            with open(tmp_path, "rb") as f:
                files = {"file": f}
                data  = {"upload_preset": "unsigned_future_me", "folder": "future-me_images"}
                resp = requests.post(url, data=data, files=files)
                resp.raise_for_status()
                secure = resp.json().get("secure_url")
                if secure:
                    image_urls.append(secure)
        finally:
            os.remove(tmp_path)

    # 4) Build preview content using raw_local to avoid timezone shifts
    try:
        raw_dt = datetime.fromisoformat(raw_local)
        display_time = raw_dt.strftime("%B %d, %Y at %I:%M %p")
    except Exception:
        display_time = raw_local

    body_html = body.replace("\n", "<br>")
    parts = [
        f"<p><em>Scheduled for {display_time}</em></p>",
        f"<p>{body_html}</p>"
    ]
    for url in image_urls:
        parts.append(f"<img src=\"{url}\" style=\"max-width:100%; margin-top:1em;\"/>")
    parts.append(
        '<button id="confirmSend" class="mt-4 bg-green-500 text-white px-4 py-2 rounded">Send</button>'
        '<button id="editMessage" class="mt-4 ml-2 bg-gray-300 text-black px-4 py-2 rounded">Edit</button>'
    )
    preview_html = "\n".join(parts)

    return jsonify({
        "preview": preview_html,
        "data": {
            "email":    email,
            "body":     body,
            "send_date": send_date_str,
            "images":   image_urls
        }
    }), 200

@app.route("/api/schedule", methods=["POST"])
def api_schedule():
    payload = request.get_json() or {}
    email         = payload.get("email")
    body          = payload.get("body")
    send_date_str = payload.get("send_date")
    image_urls    = payload.get("images", [])
    if not (email and body and send_date_str):
        return jsonify({"error": "Missing scheduling data"}), 400
    try:
        if send_date_str.endswith("Z"):
            send_date_str = send_date_str[:-1] + "+00:00"
        send_date = datetime.fromisoformat(send_date_str)
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    doc_id = save_message(
        email=email,
        body=body,
        send_date=send_date,
        image_urls=image_urls
    )
    print(f"🗓️ Scheduled message {doc_id} for {email} at {send_date.isoformat()}")
    return jsonify({"status": "scheduled", "id": doc_id}), 200

# Start scheduler once
def main():
    start_scheduler()
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    main()
