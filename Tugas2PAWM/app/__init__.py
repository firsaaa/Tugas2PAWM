from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from flask_cors import CORS
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    CORS(app, origins=["https://firsaaa.github.io"])

    @login_manager.user_loader
    def load_user(user_id):
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None

    # Register blueprints within the application context
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.progress_routes import progress_bp
    app.register_blueprint(progress_bp, url_prefix='/progress')

    @app.route('/')
    def home():
        return "Welcome to the Flask Application!"

    return app

# Create a WSGI application instance
app = create_app()
