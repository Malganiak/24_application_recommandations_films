import pandas as pd
import mysql.connector

# Connexion à la base de données
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="toor",
    database="films_database"
)

# Création d'un curseur pour exécuter des requêtes SQL
cursor = conn.cursor()

# Lecture du fichier CSV
csv_file_path = 'movies.csv'  # Assurez-vous de spécifier le chemin correct vers votre fichier CSV
df = pd.read_csv(csv_file_path)

# Conversion de la colonne 'actors' en chaînes de caractères
df['actors'] = df['actors'].apply(eval).apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

# Insertion des données dans la table films
for index, row in df.iterrows():
    insert_query = """
    INSERT INTO films (actors, contentRating, ratingCount, year, genre, img_url, directors, scenarists, id, anecdote, desc_fr, titre)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    data_tuple = (
        row['actors'], row['contentRating'], row['ratingCount'], row['year'], row['genre'],
        row['img_url'], row['directors'], row['scenarists'], row['id'], row['anecdote'], row['desc_fr'], row['titre']
    )
    cursor.execute(insert_query, data_tuple)

# Valider les modifications et fermer la connexion
conn.commit()
cursor.close()
conn.close()

print("Chargement des données terminé.")
