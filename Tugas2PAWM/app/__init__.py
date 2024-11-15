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
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    # Initialize extensions with the app
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    CORS(app, origins=["https://firsaaa.github.io", "http://127.0.0.1:5500"]) 

    @login_manager.user_loader
    def load_user(user_id):
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None

    # Register blueprints within the application context
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.progress_routes import progress_bp
    app.register_blueprint(progress_bp, url_prefix='/progress')

    @app.route('/test-mongo', methods=['GET'])
    def test_mongo():
        try:
            # Try to list collections to verify MongoDB connection
            collections = mongo.db.list_collection_names()
            return jsonify({"collections": collections}), 200
        except Exception as e:
            # Log error and return a failure message
            app.logger.error(f"MongoDB connection error: {e}")
            return jsonify({"error": "Failed to connect to MongoDB"}), 500


    @app.route('/test-mongo-connection')
    def test_mongo_connection():
        try:
            print("Attempting to connect to MongoDB...")
            # Attempt to list the collections to verify connection
            collections = mongo.db.list_collection_names()
            print("Connected successfully. Collections:", collections)
            return jsonify({"collections": collections}), 200
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            logging.error(f"MongoDB connection error: {e}")
            return jsonify({"error": "Failed to connect to MongoDB"}), 500

    

    @app.route('/')
    def home():
        return "Welcome to the Flask Application!"

    return app

# Create a WSGI application instance
app = create_app()
