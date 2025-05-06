import sqlite3

conn = sqlite3.connect('beat_users.db')
cursor = conn.cursor()

# Step 1: Create classrooms table with 4-digit ID constraint
cursor.execute('''
CREATE TABLE IF NOT EXISTS classrooms (
    id INTEGER PRIMARY KEY CHECK(length(id) = 4)
)
''')

# Step 2: Create users table, linked to classrooms
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    classroom_id INTEGER NOT NULL,
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id)
)
''')

# Step 3: Create scores table, linked to users
cursor.execute('''
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    beat_score INTEGER NOT NULL,
    date TEXT NOT NULL,
    bpm INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')


# Step 4: Insert sample classroom IDs (safe to run multiple times)
valid_classrooms = [(1234,)]
cursor.executemany('INSERT OR IGNORE INTO classrooms (id) VALUES (?)', valid_classrooms)

conn.commit()
conn.close()

print("Database initialized successfully with classrooms, users, and scores tables.")
