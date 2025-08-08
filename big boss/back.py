from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import sqlite3

app = Flask(__name__)
app.secret_key = "votre_secret_key_super_secrete"

# Mot de passe admin
ADMIN_PASSWORD = "Lifeisabitch13"

# Création DB si n'existe pas
def init_db():
    conn = sqlite3.connect('votes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('user_vote.html')

@app.route('/vote/<candidate>', methods=['POST'])
def vote(candidate):
    if candidate in ['A', 'B']:
        conn = sqlite3.connect('votes.db')
        c = conn.cursor()
        c.execute('INSERT INTO votes (candidate) VALUES (?)', (candidate,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        return "Candidat invalide", 400

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "Mot de passe incorrect", 403
    return render_template('admin_login.html')

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/results')
def results():
    conn = sqlite3.connect('votes.db')
    c = conn.cursor()
    c.execute('SELECT candidate, COUNT(*) FROM votes GROUP BY candidate')
    data = c.fetchall()
    conn.close()

    total = sum([count for _, count in data])
    results = {}
    for candidate, count in data:
        results[candidate] = {
            'count': count,
            'percent': round((count/total)*100, 2) if total > 0 else 0
        }

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
