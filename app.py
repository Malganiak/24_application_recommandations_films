from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:toor@localhost/films_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Fonction pour vérifier si l'utilisateur est connecté
def is_user_logged_in():
    return 'user_id' in session

# Chargement des embeddings
embeddings = np.load('embeddings.npy')

# Modèle de la table Users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

# Modèle de la table UserMovie
class User_movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_title = db.Column(db.String(100), nullable=False)

# Modèle de la table Films
# Modèle de la table Films
class Films(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)  # Assurez-vous que le nom de la colonne correspond à celui dans votre base de données
    actors = db.Column(db.String(100))
    contentRating = db.Column(db.String(20))
    ratingCount = db.Column(db.Integer)
    year = db.Column(db.Integer)
    genre = db.Column(db.String(100))
    img_url = db.Column(db.String(255))
    directors = db.Column(db.String(100))
    scenarists = db.Column(db.String(100))
    anecdote = db.Column(db.String(255))
    desc_fr = db.Column(db.String(255))
    user_id = db.Column(db.Integer)
    # Ajoutez d'autres colonnes si nécessaire

# Route principale
@app.route('/')
def index():
    if is_user_logged_in():
        username = User.query.get(session['user_id']).username
        return render_template('index.html', logged_in=True, username=username)
    elif 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', logged_in=True, username=user.username)
    else:
        return render_template('index.html', logged_in=False)

# Page d'inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash du mot de passe
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Création de l'utilisateur
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Inscription réussie ! Connectez-vous maintenant.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.id  # Enregistre l'ID de l'utilisateur dans la session
            flash('Connexion réussie !', 'success')
            return redirect(url_for('index'))
        else:
            flash('Échec de la connexion. Vérifiez votre nom d\'utilisateur et votre mot de passe.', 'danger')

    return render_template('login.html')

# Page de recommendations
@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    if is_user_logged_in():
        username = User.query.get(session['user_id']).username

        if request.method == 'POST':
            data = pd.read_csv('movies.csv')

            # Obtenir le titre du film saisi par l'utilisateur depuis le formulaire
            movie_title = request.form['movie_title']

            # Trouver l'indice du film dans le dataframe
            movie_index = data[data['titre'] == movie_title].index[0]

            # Obtenez l'embedding CamemBERT du film
            movie_embedding = embeddings[movie_index]

            # Calcul de la similarité cosinus avec toutes les autres descriptions
            similarities = cosine_similarity(movie_embedding.reshape(1, -1), embeddings).flatten()

            # Trier les indices par ordre décroissant de similarité
            related_movies_indices = similarities.argsort()[::-1]

            # Exclure le film lui-même de la liste des recommandations
            related_movies_indices = [i for i in related_movies_indices if i != movie_index]

            # Récupérer les titres des films recommandés
            recommendations_camembert = data['titre'].iloc[related_movies_indices][:5].tolist()

            return render_template('recommendations.html', username=username, recommendations=recommendations_camembert)

        return render_template('recommendations.html', username=username, recommendations=None)  # Pour éviter une erreur avant la soumission du formulaire
    else:
        # Redirigez vers la page de connexion si l'utilisateur n'est pas connecté
        return redirect(url_for('login'))
    
# Modification de la route /user_movies pour gérer les films de l'utilisateur connecté uniquement
@app.route('/user_movies', methods=['GET', 'POST'])
def user_movies():
    if is_user_logged_in():
        username = User.query.get(session['user_id']).username
        user_id = session['user_id']

        if request.method == 'POST':
            # Ajout d'un film pour l'utilisateur
            movie_title = request.form['movie_title']
            new_user_movie = User_movie(user_id=user_id, movie_title=movie_title)
            db.session.add(new_user_movie)
            db.session.commit()

            flash(f'Film "{movie_title}" ajouté avec succès !', 'success')

        # Récupération des films de l'utilisateur
        user_movies = User_movie.query.filter_by(user_id=user_id).all()

        return render_template('user_movies.html', username=username, user_movies=user_movies)
    else:
        # Redirigez vers la page de connexion si l'utilisateur n'est pas connecté
        return redirect(url_for('login'))
    
@app.route('/delete_movie/<int:movie_id>', methods=['POST', 'GET'])
def delete_movie(movie_id):
    if request.method == 'POST':
        if is_user_logged_in():
            movie_to_delete = User_movie.query.filter_by(id=movie_id, user_id=session['user_id']).first_or_404()
            db.session.delete(movie_to_delete)
            db.session.commit()
            flash(f'Film "{movie_to_delete.movie_title}" supprimé avec succès !', 'success')
            return redirect(url_for('user_movies'))
        else:
            # Redirigez vers la page de connexion si l'utilisateur n'est pas connecté
            return redirect(url_for('login'))
    else:
        # Gestion de la méthode GET
        # Vous pouvez afficher une page spécifique pour la confirmation de suppression, par exemple
        return render_template('confirm_delete.html', movie_id=movie_id)

# Route pour afficher la liste des films
@app.route('/films')
def films():
    if is_user_logged_in():
        username = User.query.get(session['user_id']).username

        # Récupérer tous les films depuis la base de données
        all_films = Films.query.all()

        return render_template('films.html', username=username, all_films=all_films)
    else:
        return redirect(url_for('login'))

# Page de déconnexion
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Supprime l'ID de l'utilisateur de la session
    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)