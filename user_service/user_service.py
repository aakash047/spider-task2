# user_service.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.logging_config import setup_logger
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

logger = setup_logger('user_service')

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'aakash'),
            password=os.environ.get('DB_PASSWORD', 'db_pass'),
            database='ecommerce'
        )
        if connection.is_connected():
            logger.info("Successfully connected to the database")
        return connection
    except Error as e:
        logger.error(f"Error connecting to the database: {e}")
        raise

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        logger.warning(f"Registration attempt with missing fields: {data}")
        return jsonify({"message": "Missing required fields"}), 400

    hashed_password = generate_password_hash(password)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", 
                       (username, hashed_password, email))
        conn.commit()
        logger.info(f"User registered successfully: {username}")
        return jsonify({"message": "User registered successfully"}), 201
    except Error as e:
        logger.error(f"Database error during registration: {str(e)}")
        return jsonify({"message": "An error occurred while registering"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    logger.info(f"Login attempt for user: {username}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            access_token = create_access_token(identity=username)
            logger.info(f"User logged in successfully: {username}")
            return jsonify(access_token=access_token), 200
        else:
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({"message": "Invalid credentials"}), 401
    except Error as e:
        logger.error(f"Database error during login: {str(e)}")
        return jsonify({"message": "An error occurred during login"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    logger.info(f"Profile request for user: {current_user}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email, created_at FROM users WHERE username = %s", (current_user,))
        user = cursor.fetchone()
        if user:
            logger.info(f"Profile retrieved successfully for user: {current_user}")
            return jsonify(user), 200
        else:
            logger.warning(f"Profile not found for user: {current_user}")
            return jsonify({"message": "User not found"}), 404
    except Error as e:
        logger.error(f"Database error while fetching profile: {str(e)}")
        return jsonify({"message": "An error occurred while fetching profile"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)