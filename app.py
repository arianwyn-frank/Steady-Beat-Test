from flask import Flask, render_template, request, redirect, flash, session, jsonify
import sqlite3
from datetime import date
import json

app = Flask(__name__)
DATABASE = 'beat_users.db'
app.secret_key = 'a9j4#2f^@s3!0x8Pz1$Qs8zA'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('index.html', users=users)

@app.route('/add-user', methods=['GET'])
def show_add_user_form():
    return render_template('add_user.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    classroom = request.form['classroom_id']

    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND classroom_id = ?',
        (username, classroom)
    ).fetchone()
    conn.close()

    if user:
        session['user_id'] = user['id']
        print(f"User {username} logged in.")
        return redirect('/main')
    else:
        flash(f"User {username} not found.", "error")
        return redirect('/')




@app.route('/create_user', methods=['POST'])
def create_user():
    first = request.form['first_name']
    last = request.form['last_name']
    username = request.form['username']
    classroom = request.form['classroom_id']

    if not classroom.isdigit() or len(classroom) != 4:
        flash("Error: Classroom ID must be a 4-digit number.", "error")
        return redirect('/add-user')

    conn = get_db_connection()

    # Check classroom exists
    valid = conn.execute('SELECT * FROM classrooms WHERE id = ?', (int(classroom),)).fetchone()
    if not valid:
        conn.close()
        flash(f"Error: Classroom {classroom} not found. To create a new Classroom ID, please reach out to the developer at franklyarianwyn@gmail.com", "error")
        return redirect('/add-user')

    # Insert user into users table
    try:
        conn.execute(
            'INSERT INTO users (first_name, last_name, username, classroom_id) VALUES (?, ?, ?, ?)',
            (first, last, username, classroom)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        flash("Error: That username already exists.", "error")
        return redirect('/add-user')

    conn.close()
    return redirect('/')


## test
@app.route('/main')
def main_page():
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db_connection()
    today = date.today().isoformat()
    bpm_results = conn.execute('''
        SELECT bpm FROM scores WHERE user_id = ? AND date = ?
    ''', (session['user_id'], today)).fetchall()
    conn.close()

    completed_bpms = {row['bpm'] for row in bpm_results}
    allow_100 = 100 not in completed_bpms
    allow_120 = 120 not in completed_bpms

    return render_template('main.html', allow_100=allow_100, allow_120=allow_120)

@app.route('/check_score')
def check_score():
    if 'user_id' not in session:
        return jsonify({'allowed': False, 'error': 'Not logged in'})

    bpm = request.args.get('bpm', type=int)
    today = date.today().isoformat()

    conn = get_db_connection()
    score = conn.execute(
        'SELECT * FROM scores WHERE user_id = ? AND bpm = ? AND date = ?',
        (session['user_id'], bpm, today)
    ).fetchone()
    conn.close()

    return jsonify({'allowed': score is None})


@app.route('/submit_score', methods=['POST'])
def submit_score():
    if 'user_id' not in session:
        return "User not logged in", 401

    data = request.get_json()
    presses = data.get('presses', [])
    bpm = data.get('bpm')

    if not bpm:
        return "Missing BPM", 400

    today = date.today().isoformat()

    conn = get_db_connection()
    existing = conn.execute(
        'SELECT * FROM scores WHERE user_id = ? AND bpm = ? AND date = ?',
        (session['user_id'], bpm, today)
    ).fetchone()

    if existing:
        conn.close()
        return f"You have already recorded today's score for {bpm} BPM.", 400

    expected = [i * (60000 / bpm) for i in range(32)]
    diffs = [abs(p - e) for p, e in zip(presses, expected[:len(presses)])]
    average_diff = int(sum(diffs) / len(diffs)) if diffs else 0

    conn.execute(
        'INSERT INTO scores (user_id, beat_score, date, bpm) VALUES (?, ?, ?, ?)',
        (session['user_id'], average_diff, today, bpm)
    )
    conn.commit()
    conn.close()

    return f"Score recorded: {average_diff} ms average offset"


@app.route('/teacher', methods=['GET', 'POST'])
def teacher_page():
    scores = []
    classroom_id = ''
    name_query = ''
    date_filter = ''

    if request.method == 'POST':
        classroom_id = request.form.get('classroom_id', '').strip()
        name_query = request.form.get('name_query', '').strip().lower()
        date_filter = request.form.get('date_filter', '').strip()

        query = '''
            SELECT u.first_name, u.last_name, u.username, s.bpm, s.beat_score, s.date
            FROM users u
            JOIN scores s ON u.id = s.user_id
            WHERE u.classroom_id = ?
        '''
        params = [classroom_id]

        if name_query:
            query += ' AND (LOWER(u.first_name) LIKE ? OR LOWER(u.last_name) LIKE ? OR LOWER(u.username) LIKE ?)'
            name_param = f'%{name_query}%'
            params.extend([name_param, name_param, name_param])

        if date_filter:
            query += ' AND s.date = ?'
            params.append(date_filter)

        query += ' ORDER BY s.date DESC'

        conn = get_db_connection()
        scores = conn.execute(query, params).fetchall()
        conn.close()

    return render_template('teacher.html', scores=scores,
                           classroom_id=classroom_id,
                           name_query=name_query,
                           date_filter=date_filter)



if __name__ == '__main__':
    app.run(debug=True)
