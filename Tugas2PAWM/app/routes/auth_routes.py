from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user
from app import mongo, bcrypt
from bson.objectid import ObjectId
from app.models import User
import re

auth_bp = Blueprint('auth', __name__)

# Function to validate email format
def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    users_collection = mongo.db.users  # Reference to the 'users' collection in MongoDB

    # Check if user already exists
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 400

    # Hash the password and create a new user
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = {"username": username, "email": email, "password": password_hash}

    # Insert the new user into MongoDB
    users_collection.insert_one(new_user)

    return jsonify({"message": "User registered successfully"}), 201

    

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        users_collection = mongo.db.users  # Reference to the 'users' collection in MongoDB
        user_data = users_collection.find_one({"email": email})

        if user_data:
            # Use bcrypt to check the hashed password
            if bcrypt.check_password_hash(user_data['password'], password):
                # Create a User instance using the from_mongo method
                user = User.from_mongo(user_data)
                login_user(user)  # Log the user in
                return jsonify({"message": "Logged in successfully"}), 200
            else:
                return jsonify({"error": "Invalid password"}), 401
        else:
            return jsonify({"error": "User  not found"}), 404
    except Exception as e:
        # Log the error details
        print(f"Error during login: {e}")  # Log the error for debugging
        return jsonify({"error": "An error occurred during login", "details": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200
