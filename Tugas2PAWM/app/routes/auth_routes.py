from flask import Blueprint, request, jsonify, current_app
from flask_login import logout_user
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo  # Import the initialized mongo
import jwt
import datetime
import re

auth_bp = Blueprint('auth', __name__)

# Helper function to validate email format
def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email)

# Register Route
@auth_bp.route('register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data['username']
        email = data['email']
        password = data['password']

        # Validate email format
        if not is_valid_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        # Check if the email is already registered
        if mongo.db.users.find_one({"email": email}):  # Use `mongo` to access the DB
            return jsonify({"error": "Email already registered"}), 400

        # Hash the password
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "progress": 0,
            "simulationResults": []
        }

        # Insert the new user into the database
        mongo.db.users.insert_one(new_user)
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"error": "An error occurred during registration", "details": str(e)}), 500

# Login Route
@auth_bp.route('login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        

        # Validate email format
        if not is_valid_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        # Retrieve user from database
        user_data = mongo.db.users.find_one({"email": email})  # Use `mongo` here

        if user_data:
            # Check if the password is correct
            if check_password_hash(user_data['password'], password):
                # Generate JWT token
                token = jwt.encode({
                    'user_id': str(user_data['_id']),
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                }, current_app.config['SECRET_KEY'], algorithm="HS256")

                return jsonify({"message": "Logged in successfully", "token": token}), 200
            else:
                return jsonify({"error": "Invalid password"}), 401
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"error": "An error occurred during login", "details": str(e)}), 500

# Logout Route
@auth_bp.route('logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200
