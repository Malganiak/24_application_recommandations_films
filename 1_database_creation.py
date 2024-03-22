import mysql.connector

# Connexion à la base de données (assurez-vous d'avoir installé le module mysql-connector)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="toor"
)

# Création d'un curseur pour exécuter des requêtes SQL
cursor = conn.cursor()

# Création de la base de données
database_name = "films_database"
cursor.execute(f"CREATE DATABASE {database_name};")
print(f"Requête SQL : CREATE DATABASE {database_name};")

# Sélection de la base de données nouvellement créée
cursor.execute(f"USE {database_name};")
print(f"Requête SQL : USE {database_name};")

# Fermeture du curseur et de la connexion
cursor.close()
conn.close()
