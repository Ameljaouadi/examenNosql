from app import create_app  # Importer la fonction create_app

# Appeler create_app pour obtenir l'instance de l'application et de mongo
app, mongo = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)
  # Lancer l'application Flask
