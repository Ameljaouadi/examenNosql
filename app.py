from flask import Flask,session, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import random
from flask import jsonify
from flask import Response
import matplotlib.pyplot as plt
import io
import bcrypt

import base64
app = Flask(__name__,static_folder='FrontEnd/Static',template_folder='FrontEnd/Templates')

client = MongoClient("mongodb://localhost:27017/")
db = client["mediaDB"]
# Définir une nouvelle collection pour les documents
documents = db.documents
emprunts = db.emprunts
user=db.users
app.secret_key = 'amel'

@app.route('/SideBar')
def sidebar():
    return render_template('SideBar.html')

@app.route('/NavBar')
def navbar():
    return render_template('NavBar.html')

@app.route('/AddAbonnee', methods=['GET', 'POST'])
def addAbonnees():
     # Vérifier si l'utilisateur est connecté
    if 'username' not in session:
        return redirect(url_for('login'))  # Rediriger vers la page de connexion si non connecté

    if request.method == 'POST':
        # Collecting data from the form
        data = {
            "nom": request.form.get("nom"),
            "prenom": request.form.get("prenom"),
            "email": request.form.get("email"),
            "adresse": request.form.get("adresse"),
            
            "date_inscription": request.form.get("date_inscription")
        }
        
        # Insert data into the MongoDB collection
        db.abonne.insert_one(data)
        
        # Redirect to the abonnes page after successfully adding the abonne
        return redirect(url_for('abonnees'))
    
    # If it's a GET request, just render the form
    return render_template('AddAbonnee.html')

from flask import request

@app.route('/abonnees', methods=['GET', 'POST'])
def abonnees():
     # Vérifier si l'utilisateur est connecté
    if 'username' not in session:
        return redirect(url_for('login'))  # Rediriger vers la page de connexion si non connecté

    search_query = request.args.get('search', '').strip()
    
    if search_query:
        # Requête MongoDB pour rechercher dans plusieurs champs
        abonnes = list(db.abonne.find({
            "$or": [
                {"nom": {"$regex": search_query, "$options": "i"}},
                {"prenom": {"$regex": search_query, "$options": "i"}},
                {"email": {"$regex": search_query, "$options": "i"}},
                {"adresse": {"$regex": search_query, "$options": "i"}}
            ]
        }, {"_id": 0}))
    else:
        # Si aucune recherche, renvoyer tous les abonnés
        abonnes = list(db.abonne.find({}, {"_id": 0}))

         # Ajouter les emprunts en cours pour chaque abonné
        for abonne in abonnes:
            # Recherche des emprunts en cours pour cet abonné
            emprunts_en_cours = list(db.emprunt.find({
                "email_abonne": abonne['email'],
                "status": "En Cours"  # Assurez-vous que le champ "status" ou similaire existe et indique si l'emprunt est en cours
            }))
            abonne['emprunts_en_cours'] = emprunts_en_cours
        return render_template('Abonnees.html', abonnes=abonnes)


@app.route('/delete_abonne/<email>', methods=['POST'])
def delete_abonne(email):
     # Tenter de supprimer l'abonné
    result = db.abonne.delete_one({"email": email})
    
    # Vérifier si l'abonné existait
    if result.deleted_count == 0:
        return "Aucun abonné trouvé avec cet email.", 404

    # Rediriger vers la liste des abonnés après suppression
    return redirect(url_for('abonnees'))

@app.route('/update_abonne/<email>', methods=['POST'])
def update_abonne(email):
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    adresse = request.form.get('adresse')
    date_inscription = request.form.get('date_inscription')

    abonne = db.abonne.find_one({"email": email})
    
    if not abonne:
        return jsonify({"error": "Abonné introuvable"}), 404

    db.abonne.update_one(
        {"email": email},
        {"$set": {
            "nom": nom,
            "prenom": prenom,
            "adresse": adresse,
           
            "date_inscription": date_inscription
        }}
    )

    return redirect(url_for('abonnees'))  # Redirige vers la liste des abonnés






####################catalogues#############################

@app.route('/catalogues', methods=['GET'])

def catalogues():
     # Vérifier si l'utilisateur est connecté
    if 'username' not in session:
        return redirect(url_for('login'))  # Rediriger vers la page de connexion si non connecté

    # Récupérer le paramètre de recherche
    search_query = request.args.get('search', '').strip()
    
    # Construire la requête de recherche
    query = {}
    if search_query:
        query = {
            "$or": [
                {"titre": {"$regex": search_query, "$options": "i"}},
                {"auteur": {"$regex": search_query, "$options": "i"}},
                {"type_doc": {"$regex": search_query, "$options": "i"}}
            ]
        }
    
    # Rechercher les documents correspondant au filtre
    documents = list(db.documents.find(query, {"_id": 0}))
    
    # Rendre le template avec les documents filtrés
    return render_template('Catalogue.html', documents=documents, search_query=search_query)


@app.route('/Adddocument', methods=['GET', 'POST'])
def Adddocument():
     # Vérifier si l'utilisateur est connecté
    if 'username' not in session:
        return redirect(url_for('login'))  # Rediriger vers la page de connexion si non connecté

    if request.method == 'POST':
        # Collecte des données du formulaire
        titre = request.form.get("titre")
        type_doc = request.form.get("type_doc")
        auteur = request.form.get("auteur")
        date_publication = request.form.get("date_publication")
        disponibilite = request.form.get("disponibilite")
        nbr_emprunts = request.form.get("nbr_emprunts")
        
        # Vérifier si le titre existe déjà dans la base de données
        existing_document = db.documents.find_one({"titre": titre})
        
        if existing_document:
            # Si un document avec ce titre existe déjà, afficher un message d'erreur
            return render_template('Adddocument.html', error="Le titre existe déjà dans la base de données.")
        
        # Si le titre n'existe pas, insérer le document dans la base de données
        data = {
            "titre": titre,
            "type_doc": type_doc,
            "auteur": auteur,
            "date_publication": date_publication,
            "disponibilite": disponibilite,
            "nbr_emprunts": nbr_emprunts
        }
        
        db.documents.insert_one(data)
        
        # Rediriger vers la page des documents après l'ajout
        return redirect(url_for('catalogues'))
    
    # Si la méthode est GET, afficher le formulaire
    return render_template('Adddocument.html')


@app.route('/delete_document/<titre>', methods=['POST'])
def delete_document(titre):
     # Tenter de supprimer 
    result = db.documents.delete_one({"titre": titre})
    
    # Vérifier si existait
    if result.deleted_count == 0:
        return "Aucun document trouvé avec ce titre.", 404

    # Rediriger vers la liste des abonnés après suppression
    return redirect(url_for('catalogues'))

@app.route('/update_document/<titre>',methods=['POST'])
def update_document(titre):
    
    titre = request.form.get("titre")
    type_doc = request.form.get("type_doc")
    auteur = request.form.get("auteur")
    date_publication = request.form.get("date_publication")
    disponibilite = request.form.get("disponibilite")
    nbr_emprunts = request.form.get("nbr_emprunts")


    document = db.documents.find_one({"titre": titre})
    
    if not document:
        return jsonify({"error": "document introuvable"}), 404

    db.documents.update_one(
        {"titre": titre},
        {"$set": {
            
            "titre": titre,
            "type_doc": type_doc,
            "auteur": auteur,
            "date_publication": date_publication,
            "disponibilite": disponibilite,
            "nbr_emprunts": nbr_emprunts
        }}
    )

    return redirect(url_for('catalogues')) 

########################"emprunts######################

@app.route('/emprunts', methods=['GET'])
def emprunts():
     # Vérifier si l'utilisateur est connecté
    if 'username' not in session:
        return redirect(url_for('login'))  # Rediriger vers la page de connexion si non connecté

    # Récupérer les paramètres de recherche
    search_query = request.args.get('search', '').strip()
    
    # Construire la requête de recherche
    query = {}
    if search_query:
        query = {
            "$or": [
                {"abonne.nom": {"$regex": search_query, "$options": "i"}},
                {"document.titre": {"$regex": search_query, "$options": "i"}},
                {"statut": {"$regex": search_query, "$options": "i"}}
            ]
        }
    
    # Récupérer les emprunts correspondant à la recherche
    emprunts = list(db.emprunts.find(query, {"_id": 0}))
    
    # Récupérer les informations complètes sur les abonnés et les documents
    abonnes = list(db.abonne.find({}, {"_id": 0}))
    documents = list(db.documents.find({}, {"_id": 0}))
    
    return render_template('Emprunts.html', emprunts=emprunts, abonnes=abonnes, documents=documents, search_query=search_query)
   
 

@app.route('/AddEmprunt', methods=['GET','POST'])
def AddEmprunt():
     # Vérifier si l'utilisateur est connecté
    if 'username' not in session:
        return redirect(url_for('login'))  # Rediriger vers la page de connexion si non connecté

    if request.method == 'POST':
        
         # Collecte des données du formulaire
        code_emprunt=request.form.get("code_emprunt")
        abonne_id = request.form.get("abonne")
        document_id = request.form.get("document")
        date_emprunt = request.form.get("date_emprunt")
        date_retour = request.form.get("date_retour")
        statut = request.form.get("statut")
        # Validation des dates
       
        date_emprunt_obj = datetime.strptime(date_emprunt, '%Y-%m-%d')
        date_retour_obj = datetime.strptime(date_retour, '%Y-%m-%d')
           

             

            # Vérifiez que la date de retour est après la date d'emprunt
        if date_retour_obj <= date_emprunt_obj:
            flash(("danger", "La date de retour prévue doit être après la date d’emprunt."))
            return redirect(url_for('AddEmprunt'))
            
            
        
           
           
        
          # Récupérer les informations complètes sur l'abonné et le document
        abonne = db.abonne.find_one({"_id": ObjectId(abonne_id)})
        document = db.documents.find_one({"_id": ObjectId(document_id)})
        db.emprunts.insert_one({
            "abonne": {
                "_id": abonne["_id"],
                "nom": abonne["nom"],
                
            },
            "document": {
                "_id": document["_id"],
                "titre": document["titre"]
            },
            "date_emprunt": date_emprunt,
            "date_retour": date_retour,
            "statut": statut,
            "code_emprunt":code_emprunt
        })
   
        return redirect(url_for('emprunts'))
    # Si la méthode est GET, afficher le formulaire
    abonnes = list(db.abonne.find({}) )
    documents=list(db.documents.find({})) 
   

    return render_template('AddEmprunt.html',abonnes=abonnes, documents=documents)

# @app.route('/update_emprunt/<id>', methods=[ 'POST'])
# def update_emprunt(id):
#     emprunt = db.emprunts.find_one({"_id": ObjectId(id)})
   
#         # Collecte des données du formulaire
#     abonne_id = request.form.get("abonne")
#     document_id = request.form.get("document")
#     date_emprunt = request.form.get("date_emprunt")
#     date_retour = request.form.get("date_retour")
#     statut = request.form.get("statut")
#         # Validation des dates (identique à AddEmprunt)
       

            
#         #     # Vérifiez que la date de retour est après la date d'emprunt
#         # if date_emprunt <= date_retour:
#         #     flash(("danger", "La date de retour prévue doit être après la date d’emprunt."))
#         #     return redirect(url_for('update_emprunt', id=id))

           
       
#         # Récupérer les informations complètes sur l'abonné et le document
#     abonne = db.abonne.find_one({"_id": ObjectId(abonne_id)})
#     document = db.documents.find_one({"_id": ObjectId(document_id)})

#         # Mettre à jour l'emprunt dans la base de données
#     db.emprunts.update_one(
#         {"_id": ObjectId(id)},
#         {
#             "$set": {
#                 "abonne": {
#                     "_id": abonne["_id"],
#                     "nom": abonne["nom"],
#                 },
#                 "document": {
#                     "_id": document["_id"],
#                     "titre": document["titre"],
#                 },
#                 "date_emprunt": date_emprunt,
#                 "date_retour": date_retour,
#                 "statut": statut
#                 }
#             }
#         )

#     return redirect(url_for('emprunts'))

#     # Si la méthode est GET, afficher le formulaire avec les données de l'emprunt
#     abonnes = list(db.abonne.find({}))
#     documents = list(db.documents.find({}))
#     return render_template('EditEmprunt.html', emprunt=emprunt, abonnes=abonnes, documents=documents)


@app.route('/update_emprunt/<code_emprunt>', methods=['POST'])

def update_emprunt(code_emprunt):
     # Vérifier si l'utilisateur est connecté
    if 'username' not in session:
        return redirect(url_for('login'))  # Rediriger vers la page de connexion si non connecté


    code_emprunt=request.form.get("code_emprunt")
    abonne_id = request.form.get('abonne')
    document_id = request.form.get('document')
    date_emprunt = request.form.get('date_emprunt')
    date_retour = request.form.get('date_retour')
    statut = request.form.get('statut')

    emprunt = db.emprunts.find_one({"code_emprunt": code_emprunt})    
   
    if not emprunt:
        return jsonify({"error": "Emprunt introuvable"}), 404
    # Récupérer l'abonné et le document complets
    abonne = db.abonne.find_one({"_id": ObjectId(abonne_id)})
    if not abonne:
       return jsonify({"error": "Abonné introuvable"}), 404
    document = db.documents.find_one({"_id": ObjectId(document_id)})
    if not document:
       return jsonify({"error": "Document introuvable"}), 404

    db.emprunts.update_one(
        {"code_emprunt": code_emprunt},
        {"$set": {
            "abonne": {
                "_id": abonne["_id"],
                "nom": abonne["nom"],
            },
            "document": {
                "_id": document["_id"],
                "titre": document["titre"],
            },
            "date_emprunt": date_emprunt,
            "date_retour": date_retour,
            "statut": statut,
        }}
    )
    print(request.form)

    return redirect(url_for('emprunts')) 

@app.route('/delete_emprunt/<code_emprunt>', methods=['POST'])
def delete_emprunt(code_emprunt):
    result = db.emprunts.delete_one({"code_emprunt": code_emprunt})  # Filtre correct
    
    if result.deleted_count == 0:
        return "Aucun emprunt trouvé avec ce code.", 404

    return redirect(url_for('emprunts'))



##################dashbord####################################""


@app.route('/')
def Dashbord():

     # Vérifier si l'utilisateur est connecté
    if 'username' not in session:
        return redirect(url_for('login'))  # Rediriger vers la page de connexion si non connecté


    # Récupérer le nombre total d'abonnés
    total_abonnes = db.abonne.count_documents({})
    
    # Récupérer le nombre total de documents
    total_documents = db.documents.count_documents({})
    
    # Récupérer le nombre total d'emprunts
    total_emprunts = db.emprunts.count_documents({})
    
    # Récupérer le document le plus emprunté
    most_borrowed = db.emprunts.aggregate([
        {"$group": {"_id": "$document.titre", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ])
    most_borrowed = list(most_borrowed)
    most_borrowed_title = most_borrowed[0]["_id"] if most_borrowed else "Aucun emprunt"
   
    # Générer l'histogramme des emprunts par document
    emprunts = db.emprunts.find()
    documents_counts = {}
    for emprunt in emprunts:
        titre = emprunt['document']['titre']
        documents_counts[titre] = documents_counts.get(titre, 0) + 1

    # Données pour l'histogramme des emprunts
    titres = list(documents_counts.keys())
    valeurs = list(documents_counts.values())

    # Créer l'histogramme des emprunts par document
    plt.figure(figsize=(10, 6))
    plt.bar(titres, valeurs, color='skyblue')
    plt.xlabel('Documents')
    plt.ylabel('Nombre d\'emprunts')
    plt.title('Histogramme des emprunts par document')
    plt.xticks(rotation=45, ha='right')
    
    # Convertir le graphique des emprunts en image pour le HTML
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # Générer l'histogramme des abonnés par mois
    abonnements = db.abonne.find()
    abonnements_counts = {}
    for abonne in abonnements:
        # Convertir la date d'inscription en datetime
        date_str = abonne['date_inscription']  # Supposons que c'est une chaîne
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Convertir en datetime
        mois = date_obj.strftime('%Y-%m')  # Format mois/année
        abonnements_counts[mois] = abonnements_counts.get(mois, 0) + 1

    # Données pour l'histogramme des abonnés
    mois_abonnements = list(abonnements_counts.keys())
    count_abonnements = list(abonnements_counts.values())

    # Créer l'histogramme des abonnés
    plt.figure(figsize=(10, 6))
    plt.bar(mois_abonnements, count_abonnements, color='lightgreen')
    plt.xlabel('Mois')
    plt.ylabel('Nombre d\'abonnés')
    plt.title('Histogramme des abonnés par mois')
    plt.xticks(rotation=45, ha='right')
    
    # Convertir le graphique des abonnés en image pour le HTML
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url_abonnes = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # Générer l'histogramme des emprunts par mois
    emprunts_par_mois = {}
    for emprunt in db.emprunts.find():
        # Convertir la date d'emprunt en datetime
        date_str = emprunt['date_emprunt']  # Supposons que c'est une chaîne
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Convertir en datetime
        mois = date_obj.strftime('%Y-%m')  # Format mois/année
        emprunts_par_mois[mois] = emprunts_par_mois.get(mois, 0) + 1

    # Données pour l'histogramme des emprunts par mois
    mois_emprunts = list(emprunts_par_mois.keys())
    count_emprunts = list(emprunts_par_mois.values())

    # Créer l'histogramme des emprunts par mois
    plt.figure(figsize=(10, 6))
    plt.bar(mois_emprunts, count_emprunts, color='orange')
    plt.xlabel('Mois')
    plt.ylabel('Nombre d\'emprunts')
    plt.title('Histogramme des emprunts par mois')
    plt.xticks(rotation=45, ha='right')

    # Convertir le graphique des emprunts par mois en image pour le HTML
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url_emprunts = base64.b64encode(img.getvalue()).decode()
    plt.close()


    # Passer les données au template
    return render_template(
        'Dashbord.html', 
        total_abonnes=total_abonnes,
        total_documents=total_documents,
        total_emprunts=total_emprunts,
        most_borrowed_title=most_borrowed_title,
        plot_url=plot_url,
        plot_url_abonnes=plot_url_abonnes,
        plot_url_emprunts=plot_url_emprunts
    )
 
@app.route('/histogrammes', methods=['GET'])
def histogrammes():
    # Exemple : Générer un histogramme pour le nombre d'emprunts par abonné
    emprunts = list(db.emprunts.find({}))
    abonnes = [emprunt['abonne']['nom'] for emprunt in emprunts]
    
    # Compter les emprunts par abonné
    abonne_counts = {abonne: abonnes.count(abonne) for abonne in set(abonnes)}

    # Créer un histogramme
    plt.figure(figsize=(10, 6))
    plt.bar(abonne_counts.keys(), abonne_counts.values(), color='skyblue')
    plt.xlabel('Abonnés')
    plt.ylabel('Nombre d\'emprunts')
    plt.title('Histogramme des emprunts par abonné')
    plt.xticks(rotation=45, ha='right')

    # Sauvegarder l'image dans un buffer pour la renvoyer via HTTP
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Encoder l'image en base64 pour l'intégrer dans une page HTML ou la renvoyer directement
    return Response(buf.getvalue(), mimetype='image/png')
  
#login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form['username']
        password = request.form['password']
         # Trouver l'utilisateur dans la base de données
        userr = user.find_one({"username": username})

        if userr:
            # Vérifier le mot de passe (assurez-vous que le mot de passe est stocké haché)
            if bcrypt.checkpw(password.encode('utf-8'), userr['password']):
                # Créer une session pour l'utilisateur connecté
                session['username'] = username
                return redirect(url_for('Dashbord'))
            else:
                return "Invalid credentials, please try again"
        else:
            return "User not found, please try again"
    return render_template('login.html')

# Route pour la déconnexion
@app.route('/logout')
def logout():
    # Supprimer les données de session
    session.clear()
    # Rediriger vers la page de connexion
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
