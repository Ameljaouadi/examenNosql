from flask import Flask
from flask_pymongo import PyMongo

mongo = None 

def create_app():
    global mongo
    app = Flask(__name__)

    # Load configuration from config.py
    app.config.from_pyfile('Config.py')

    # Initialize PyMongo
    mongo = PyMongo(app)

    # Register the Blueprint for routes
    from .routes import abonne_bp
    app.register_blueprint(abonne_bp,url_prefix='/api')

    return app, mongo
