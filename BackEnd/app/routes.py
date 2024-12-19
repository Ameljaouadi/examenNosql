from flask import Blueprint, request, jsonify
from datetime import datetime

from pymongo import MongoClient

# Configuration MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['mediaDB']
abonnes = db.abonne 
documents = db.documents
# Créer un Blueprint pour les routes
abonne_bp = Blueprint('abonne', __name__)
document_bp = Blueprint('documents', __name__)
@abonne_bp.route('/AddAbonnee', methods=['POST'])
def create_abonne():
    try:
        # Check if the request contains JSON data
        if request.is_json:
            data = request.get_json()
        else:
            return jsonify({"error": "Invalid input, JSON required"}), 400

        # Validate required fields
        required_fields = ["nom", "prenom", "email", "adresse", "date_inscription"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Ensure the 'date_inscription' is a valid date string
        try:
            date_inscription = datetime.strptime(data["date_inscription"], "%d/%m/%Y")
        except ValueError:
            return jsonify({"error": "Invalid date format, expected YYYY/MM/DD"}), 400
        
        # Prepare the data to be inserted
        new_abonne = {
            "nom": data["nom"],
            "prenom": data["prenom"],
            "email": data["email"],
            "adresse": data["adresse"],
            "date_inscription": date_inscription
        }

        # Check if an abonne with the same email already exists
        if abonnes.find_one({"email": new_abonne["email"]}):
            return jsonify({"error": "An abonne with this email already exists"}), 400

        # Insert the new abonne
        abonnes.insert_one(new_abonne)
        
        # Return a success response
        return jsonify({"message": "Abonne created successfully!"}), 201

    except Exception as e:
        # Return error if something goes wrong
        return jsonify({"error": str(e)}), 500


@abonne_bp.route('/abonne', methods=['GET'])
def get_abonnes():
    abonnes = list(db.abonne.find({}, {"_id": 0}))
    return jsonify(abonnes), 200

@abonne_bp.route('/abonne/<email>', methods=['PUT'])
def update_abonne(email):
    # Récupérer les données JSON envoyées dans la requête
    data = request.json

    if not data:
        return jsonify({"error": "Aucune donnée fournie pour la mise à jour"}), 400

    # Validation des données : suppression des clés vides
    valid_data = {key: value for key, value in data.items() if value is not None and value != ""}

    if not valid_data:
        return jsonify({"error": "Aucun champ valide fourni pour la mise à jour"}), 400

    # Mise à jour des champs dans MongoDB
    result = db.abonne.update_one({"email": email}, {"$set": valid_data})

    # Vérifiez si un document a été trouvé et mis à jour
    if result.matched_count == 0:
        return jsonify({"error": f"Aucun abonné trouvé avec l'email '{email}'"}), 404

    if result.modified_count == 0:
        return jsonify({"message": "Aucun changement détecté dans les données"}), 200

    return jsonify({"message": "Abonné mis à jour avec succès !"}), 200


@abonne_bp.route('/abonne/<email>', methods=['DELETE'])
def delete_abonne(email):
    db.abonne.delete_one({"email": email})
    return jsonify({"message": "Abonné supprimé avec succès !"}), 200

@abonne_bp.route('/abonne/delete', methods=['DELETE'])
def delete_all():
    try:
        # Suppression de tous les abonnés dans la collection
        result = db.abonne.delete_many({})

        # Vérifier si des abonnés ont été supprimés
        if result.deleted_count > 0:
            return jsonify({"message": f"{result.deleted_count} abonnés supprimés avec succès !"}), 200
        else:
            return jsonify({"message": "Aucun abonné trouvé à supprimer."}), 404

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la suppression des abonnés: {str(e)}"}), 500



@document_bp.route('/delete_document/<titre>', methods=['POST'])
def delete_document(titre):
     # Tenter de supprimer 
    result = db.abonne.delete_one({"titre": titre})
    
    # Vérifier si existait
    if result.deleted_count == 0:
        return "Aucun document trouvé avec ce titre.", 404

    # Rediriger vers la liste des abonnés après suppression
    return redirect(url_for('catalogues'))

@document_bp.route('/document/delete', methods=['DELETE'])
def delete_all_documents():
    try:
        # Suppression de tous les documents dans la collection
        result = documents.delete_many({})

        # Vérifier si des documents ont été supprimés
        if result.deleted_count > 0:
            return jsonify({"message": f"{result.deleted_count} documents supprimés avec succès !"}), 200
        else:
            return jsonify({"message": "Aucun document trouvé à supprimer."}), 404

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la suppression des documents: {str(e)}"}), 500

