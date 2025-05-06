import sqlite3

conn = sqlite3.connect('beat_users.db')
cursor = conn.cursor()

# Print all tables
print("Tables in database:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
for table in cursor.fetchall():
    print(table[0])

# Show schema for scores table
print("\nSchema for scores table:")
cursor.execute("PRAGMA table_info(scores);")
for row in cursor.fetchall():
    print(row)

# Optional: Show recent entries
print("\nRecent scores:")
cursor.execute("SELECT * FROM scores ORDER BY id DESC LIMIT 5;")
for row in cursor.fetchall():
    print(row)

conn.close()
