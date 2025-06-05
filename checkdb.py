import sqlite3

with sqlite3.connect("database.db") as conn:
    c = conn.cursor()
    c.execute("SELECT * FROM messages")
    rows = c.fetchall()

    print("Current messages in database:")
    for row in rows:
        print(row)
