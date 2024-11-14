# app/__init__.py
from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from flask_cors import CORS
from bson import ObjectId
from app.models import User


# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = 'b0d659cdba453b7b7af7746dad3c6f8aa64b89400d4948d7'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Initialize extensions with the app
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    CORS(app, origins=["http://127.0.0.1:5500", "https://firsaaa.github.io"])

    @login_manager.user_loader
    def load_user(user_id):
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Register the progress blueprint
    from app.routes.progress_routes import progress_bp
    app.register_blueprint(progress_bp, url_prefix='/progress')

    # Optional: Add a simple home route for testing
    @app.route('/')
    def home():
        return "Welcome to the Flask Application!"

    return app
