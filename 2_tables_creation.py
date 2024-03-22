import mysql.connector

# Connexion à la base de données (assurez-vous d'avoir installé le module mysql-connector)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="toor",
    database="films_database"
)

# Création d'un curseur pour exécuter des requêtes SQL
cursor = conn.cursor()

# Création de la table utilisateurs
utilisateurs_table_query = """
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
cursor.execute(utilisateurs_table_query)
print("\nRequête SQL pour la table utilisateurs :")
print(utilisateurs_table_query)

# Création de la table films avec ajout de la colonne user_id et la clé étrangère
films_table_query = """
CREATE TABLE films (
    id VARCHAR(255) PRIMARY KEY,
    actors VARCHAR(255),
    contentRating VARCHAR(255),
    ratingCount INT,
    year DATE,
    genre VARCHAR(255),
    img_url VARCHAR(255),
    directors VARCHAR(255),
    scenarists VARCHAR(255),
    anecdote TEXT,
    desc_fr TEXT,
    titre VARCHAR(255),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES utilisateurs(id)
);
"""

cursor.execute(films_table_query)
print("Requête SQL pour la table films :")
print(films_table_query)

# Fermeture du curseur et de la connexion
cursor.close()
conn.close()
