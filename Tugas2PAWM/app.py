from quart import Quart, request, jsonify
import asyncpg
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Quart(__name__)

async def get_db_connection():
    return await asyncpg.create_pool(dsn=Config.DATABASE_URL)

@app.route('/auth/register', methods=['POST'])
async def register():
    data = await request.get_json()
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400
    username = data['username']
    email = data['email']
    password = data['password']
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    pool = await get_db_connection()
    async with pool.acquire() as connection:
        result = await connection.fetchrow("SELECT * FROM users WHERE email = $1", email)
        if result:
            return jsonify({"message": "Email already exists"}), 400
        await connection.execute(
            "INSERT INTO users (username, email, password) VALUES ($1, $2, $3)",
            username, email, hashed_password
        )
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/auth/login', methods=['POST'])
async def login():
    data = await request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400
    email = data['email']
    password = data['password']
    pool = await get_db_connection()
    async with pool.acquire() as connection:
        user = await connection.fetchrow("SELECT * FROM users WHERE email = $1", email)
    if not user:
        return jsonify({"message": "Invalid email or password"}), 401
    stored_password = user['password']
    if not check_password_hash(stored_password, password):
        return jsonify({"message": "Invalid email or password"}), 401
    return jsonify({"message": "Login successful"}), 200

if __name__ == "__main__":
    app.run(debug=True)