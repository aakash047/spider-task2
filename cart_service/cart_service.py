# cart_service.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import mysql.connector
from mysql.connector import Error
import requests
from common.logging_config import setup_logger

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
jwt = JWTManager(app)

logger = setup_logger('cart_service')

PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://localhost:5002')

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'your_username'),
            password=os.environ.get('DB_PASSWORD', 'your_password'),
            database='ecommerce'
        )
    except Error as e:
        logger.error(f"Error connecting to the database: {e}")
        raise


@app.route('/cart/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    current_user = get_jwt_identity()
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        logger.warning(f"Attempt to add to cart without product_id: {data}")
        return jsonify({"message": "Product ID is required"}), 400

    logger.info(f"Adding product {product_id} to cart for user: {current_user}")


    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, get or create user_id based on the username
        cursor.execute("SELECT id FROM users WHERE username = %s", (current_user,))
        user_result = cursor.fetchone()
        if user_result:
            user_id = user_result[0]
        else:
            cursor.execute("INSERT INTO users (username) VALUES (%s)", (current_user,))
            user_id = cursor.lastrowid
        
        # Check if the item is already in the cart
        cursor.execute("SELECT * FROM cart_items WHERE user_id = %s AND product_id = %s", 
                       (user_id, product_id))
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Update quantity if the item is already in the cart
            new_quantity = existing_item[3] + quantity
            cursor.execute("UPDATE cart_items SET quantity = %s WHERE user_id = %s AND product_id = %s",
                           (new_quantity, user_id, product_id))
            logger.info(f"Updated quantity for product {product_id} in cart for user {current_user}")
        else:
            # Add new item to the cart
            cursor.execute("INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                           (user_id, product_id, quantity))
            logger.info(f"Added new product {product_id} to cart for user {current_user}")
        
        conn.commit()
        return jsonify({"message": "Item added to cart"}), 201
    except Error as e:
        logger.error(f"Database error while adding item to cart for user {current_user}: {str(e)}")
        return jsonify({"message": "An error occurred while adding item to cart"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)