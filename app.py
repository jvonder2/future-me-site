from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename
from scheduler import start_scheduler
from datetime import datetime
import pytz

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Setup DB
def init_db():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            send_date TEXT NOT NULL,
            image_path TEXT,
            sent INTEGER DEFAULT 0
        )''')

# Call these on startup
init_db()
start_scheduler()

# Serve the frontend
@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

# API endpoint to schedule a message
@app.route('/api/send-later', methods=['POST'])
def schedule_email():
    email = request.form['email']
    message = request.form['message']
    send_date_str = request.form['send_date']
    image = request.files.get('image')

    # Convert to UTC before storing
    local = pytz.timezone("America/New_York")
    local_dt = local.localize(datetime.strptime(send_date_str, "%Y-%m-%dT%H:%M"))
    utc_dt = local_dt.astimezone(pytz.utc)
    send_date_utc = utc_dt.strftime("%Y-%m-%d %H:%M:%S")

    image_path = None
    if image and image.filename:
        # Sanitize the filename
        filename = secure_filename(image.filename)

        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        full_save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(full_save_path)

        # Store only the filename in the database
        image_path = filename

    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO messages (email, message, send_date, image_path) VALUES (?, ?, ?, ?)",
            (email, message, send_date_utc, image_path)
        )
        conn.commit()

    print(f"Received message for {email} to send at {send_date_utc} (Image: {image_path})")
    return jsonify({'status': 'Message scheduled!'})

# Local dev only
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
