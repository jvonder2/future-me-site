from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from scheduler import start_scheduler

app = Flask(__name__)

# Setup DB (run this once)
def init_db():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            send_date TEXT NOT NULL,
            sent INTEGER DEFAULT 0
        )''')

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
    data = request.json
    email = data['email']
    message = data['message']
    send_date = data['send_date']

    print(f"📩 Received message for {email} to send at {send_date}")


    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO messages (email, message, send_date) VALUES (?, ?, ?)",
                  (email, message, send_date))
        conn.commit()

    return jsonify({'status': 'Message scheduled!'})

# Start the app and background scheduler
if __name__ == '__main__':
    init_db()
    start_scheduler()
    app.run(debug=True, use_reloader=False)
