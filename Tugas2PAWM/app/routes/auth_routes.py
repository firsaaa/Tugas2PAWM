from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user
from app import mongo, bcrypt
from bson.objectid import ObjectId
from app.models import User
import re
from flask_cors import CORS, cross_origin

auth_bp = Blueprint('auth', __name__)
CORS(auth_bp, origins="http://127.0.0.1:5500")

def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    users_collection = mongo.db.users

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = {"username": username, "email": email, "password": password_hash}

    users_collection.insert_one(new_user)
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        users_collection = mongo.db.users
        user_data = users_collection.find_one({"email": email})

        if user_data:
            if bcrypt.check_password_hash(user_data['password'], password):
                user = User.from_mongo(user_data)
                login_user(user)
                return jsonify({"message": "Logged in successfully"}), 200
            else:
                return jsonify({"error": "Invalid password"}), 401
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"error": "An error occurred during login", "details": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200
