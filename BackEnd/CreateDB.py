from pymongo import MongoClient
import bcrypt
# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")

# Specify the database name
db_name = "mediaDB"  
db = client[db_name]

# # Create a collection and insert a sample document
# #db.users.insert_one({"name": "amel", "email": "amel@gmail.com"})
# db.documents.insert_one({ 
#     "titre": "titanic", 
#     "type": "drama",
#      "auteur":"houyem",
#       "date_publication":"10/05/2014",
#        "disponibilite":"oui"})
db.abonne.insert_one({
    "nom": "maissa", 
    "prenom": "daas", 
    "email": "maissa@gmail.com",
    
    "adresse": "nabeul", 
    "date_inscription": "18/12/2024"
    
})
# Create the 'users' collection with a sample admin user
# password = "admin123"
# hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# # Insérer l'utilisateur dans la base de données
# db.users.insert_one({
#     "username": "admin",
#     "email": "admin@example.com",
#     "password": hashed_password,
#     "date_created": "19/11/2024"
# })
# print(f"Database '{db_name}' created successfully with a sample document.")