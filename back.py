from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import sqlite3
import os

app = Flask(__name__)
# Utilisez une clé secrète forte et générée aléatoirement en production
app.secret_key = "votre_secret_key_super_secrete_et_unique_pour_bigboss"

# Mot de passe admin
ADMIN_PASSWORD = "Lifeisabitch13"

# Chemin vers le dossier des templates
# Assurez-vous que les fichiers HTML sont dans un dossier 'templates' au même niveau que 'back.py'
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app.template_folder = template_dir

# Création de la base de données si elle n'existe pas
def init_db():
    conn = sqlite3.connect('votes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Route pour la page d'accueil (bigboss.html)
@app.route('/')
def index():
    # Flask cherche automatiquement les templates dans le dossier configuré (ici 'templates')
    return render_template('bigboss.html')

# Route pour voter pour un candidat
@app.route('/vote/<candidate_name>', methods=['POST'])
def vote(candidate_name):
    # Liste des candidats valides (à adapter si vous avez plus ou moins de candidats)
    valid_candidates = ["Nom du Candidat 1", "Nom du Candidat 2", "Nom du Candidat 3", "Nom du Candidat 4"]
    if candidate_name in valid_candidates:
        try:
            conn = sqlite3.connect('votes.db')
            c = conn.cursor()
            c.execute('INSERT INTO votes (candidate) VALUES (?)', (candidate_name,))
            conn.commit()
            conn.close()
            # Retourne une réponse JSON pour le frontend
            return jsonify({"success": True, "message": f"Vote enregistré pour {candidate_name}"}), 200
        except Exception as e:
            print(f"Erreur lors de l'enregistrement du vote : {e}")
            return jsonify({"success": False, "message": "Erreur lors de l'enregistrement du vote"}), 500
    else:
        return jsonify({"success": False, "message": "Candidat invalide"}), 400

# Route pour la connexion administrateur
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            # Ajout d'un message d'erreur pour l'utilisateur
            return render_template('admin_login.html', error="Mot de passe incorrect")
    return render_template('admin_login.html')

# Route pour le tableau de bord administrateur
@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

# Route pour obtenir les résultats des votes (API)
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
    # Assurez-vous que tous les candidats sont présents, même avec 0 vote
    all_candidates = ["Nom du Candidat 1", "Nom du Candidat 2", "Nom du Candidat 3", "Nom du Candidat 4"]
    for cand in all_candidates:
        if cand not in results:
            results[cand] = {'count': 0, 'percent': 0.0}

    return jsonify(results)

if __name__ == '__main__':
    # Pour le déploiement en production, n'utilisez PAS debug=True
    # Utilisez un serveur WSGI comme Gunicorn ou uWSGI
    app.run(host='0.0.0.0', port=5000, debug=True)
