from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config.Config')
mongo = PyMongo(app)
login_manager = LoginManager(app)

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])  # MongoDB uses '_id' field, so we convert it to a string for compatibility
        self.username = user_data["username"]
        self.email = user_data["email"]
        self.password = user_data['password']
        # for progress
        self.progress = user_data.get("progress", 0)
        self.simulationResults = user_data.get("simulationResults", [])
        self.additionalInfo = user_data.get("additionalInfo", {})
    
    @staticmethod
    def from_mongo(user_data):
        return User(user_data) if user_data else None

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": user_id})
    return User.from_mongo(user_data)

@app.route('/register', methods=['POST'])
def register():
    users = mongo.db.users
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = generate_password_hash(data['password'])

    if users.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 400

    users.insert_one({"username": username, "email": email, "password": password})
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    data = request.get_json()
    user_data = users.find_one({"email": data['email']})

    if user_data and check_password_hash(user_data['password'], data['password']):
        user = User.from_mongo(user_data)  # Create User instance for login_user
        login_user(user)
        return jsonify({"message": "Logged in successfully"}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
