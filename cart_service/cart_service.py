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
            database='ecommerce_carts'
        )
    except Error as e:
        logger.error(f"Error connecting to the database: {e}")
        raise

@app.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    current_user = get_jwt_identity()
    logger.info(f"Fetching cart for user: {current_user}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cart_items WHERE user_id = %s", (current_user,))
        cart_items = cursor.fetchall()
        
        for item in cart_items:
            product_response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{item['product_id']}")
            if product_response.status_code == 200:
                item['product_details'] = product_response.json()
            else:
                item['product_details'] = None
                logger.warning(f"Failed to fetch product details for product_id: {item['product_id']}")

        logger.info(f"Successfully fetched cart for user: {current_user}")
        return jsonify(cart_items), 200
    except Error as e:
        logger.error(f"Database error while fetching cart for user {current_user}: {str(e)}")
        return jsonify({"message": "An error occurred while fetching the cart"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

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

    # Check product availability
    product_response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
    if product_response.status_code != 200:
        logger.warning(f"Product not found: {product_id}")
        return jsonify({"message": "Product not found"}), 404

    product = product_response.json()
    if product['stock'] < quantity:
        logger.warning(f"Insufficient stock for product {product_id}. Requested: {quantity}, Available: {product['stock']}")
        return jsonify({"message": "Insufficient stock"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the item is already in the cart
        cursor.execute("SELECT * FROM cart_items WHERE user_id = %s AND product_id = %s", 
                       (current_user, product_id))
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Update quantity if the item is already in the cart
            new_quantity = existing_item[3] + quantity
            cursor.execute("UPDATE cart_items SET quantity = %s WHERE user_id = %s AND product_id = %s",
                           (new_quantity, current_user, product_id))
            logger.info(f"Updated quantity for product {product_id} in cart for user {current_user}")
        else:
            # Add new item to the cart
            cursor.execute("INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                           (current_user, product_id, quantity))
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

@app.route('/cart/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    current_user = get_jwt_identity()
    logger.info(f"Removing item {item_id} from cart for user: {current_user}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart_items WHERE id = %s AND user_id = %s", (item_id, current_user))
        conn.commit()
        if cursor.rowcount > 0:
            logger.info(f"Successfully removed item {item_id} from cart for user {current_user}")
            return jsonify({"message": "Item removed from cart"}), 200
        else:
            logger.warning(f"Item {item_id} not found in cart for user {current_user}")
            return jsonify({"message": "Item not found in cart"}), 404
    except Error as e:
        logger.error(f"Database error while removing item from cart for user {current_user}: {str(e)}")
        return jsonify({"message": "An error occurred while removing item from cart"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/cart/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    current_user = get_jwt_identity()
    data = request.get_json()
    quantity = data.get('quantity')

    if not quantity or quantity < 1:
        logger.warning(f"Invalid quantity for cart update: {quantity}")
        return jsonify({"message": "Invalid quantity"}), 400

    logger.info(f"Updating quantity for item {item_id} in cart for user: {current_user}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First, get the current cart item
        cursor.execute("SELECT * FROM cart_items WHERE id = %s AND user_id = %s", (item_id, current_user))
        cart_item = cursor.fetchone()
        
        if not cart_item:
            logger.warning(f"Item {item_id} not found in cart for user {current_user}")
            return jsonify({"message": "Item not found in cart"}), 404

        # Check product availability
        product_response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{cart_item['product_id']}")
        if product_response.status_code != 200:
            logger.warning(f"Product not found: {cart_item['product_id']}")
            return jsonify({"message": "Product not found"}), 404

        product = product_response.json()
        if product['stock'] < quantity:
            logger.warning(f"Insufficient stock for product {cart_item['product_id']}. Requested: {quantity}, Available: {product['stock']}")
            return jsonify({"message": "Insufficient stock"}), 400

        # Update the quantity
        cursor.execute("UPDATE cart_items SET quantity = %s WHERE id = %s AND user_id = %s", 
                       (quantity, item_id, current_user))
        conn.commit()
        
        logger.info(f"Successfully updated quantity for item {item_id} in cart for user {current_user}")
        return jsonify({"message": "Cart item updated"}), 200
    except Error as e:
        logger.error(f"Database error while updating cart item for user {current_user}: {str(e)}")
        return jsonify({"message": "An error occurred while updating cart item"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/cart/clear', methods=['POST'])
@jwt_required()
def clear_cart():
    current_user = get_jwt_identity()
    logger.info(f"Clearing cart for user: {current_user}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart_items WHERE user_id = %s", (current_user,))
        conn.commit()
        logger.info(f"Successfully cleared cart for user {current_user}")
        return jsonify({"message": "Cart cleared successfully"}), 200
    except Error as e:
        logger.error(f"Database error while clearing cart for user {current_user}: {str(e)}")
        return jsonify({"message": "An error occurred while clearing the cart"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/cart/checkout', methods=['POST'])
@jwt_required()
def checkout():
    current_user = get_jwt_identity()
    logger.info(f"Initiating checkout for user: {current_user}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all items in the cart
        cursor.execute("SELECT * FROM cart_items WHERE user_id = %s", (current_user,))
        cart_items = cursor.fetchall()
        
        if not cart_items:
            logger.warning(f"Attempted checkout with empty cart for user {current_user}")
            return jsonify({"message": "Cart is empty"}), 400

        total_price = 0
        order_items = []

        # Verify stock and calculate total price
        for item in cart_items:
            product_response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{item['product_id']}")
            if product_response.status_code != 200:
                logger.warning(f"Product not found during checkout: {item['product_id']}")
                return jsonify({"message": f"Product {item['product_id']} not found"}), 404

            product = product_response.json()
            if product['stock'] < item['quantity']:
                logger.warning(f"Insufficient stock for product {item['product_id']} during checkout")
                return jsonify({"message": f"Insufficient stock for product {product['name']}"}), 400

            item_price = product['price'] * item['quantity']
            total_price += item_price
            order_items.append({
                "product_id": item['product_id'],
                "quantity": item['quantity'],
                "price": item_price
            })

        # Here you would typically integrate with a payment service
        # For this example, we'll assume the payment is successful

        # Update product stock
        for item in order_items:
            requests.put(f"{PRODUCT_SERVICE_URL}/products/{item['product_id']}", 
                         json={"stock_change": -item['quantity']})

        # Clear the cart
        cursor.execute("DELETE FROM cart_items WHERE user_id = %s", (current_user,))
        
        # Create an order (you would typically have a separate order service for this)
        cursor.execute("INSERT INTO orders (user_id, total_price) VALUES (%s, %s)", (current_user, total_price))
        order_id = cursor.lastrowid

        for item in order_items:
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                           (order_id, item['product_id'], item['quantity'], item['price']))

        conn.commit()
        logger.info(f"Checkout successful for user {current_user}. Order ID: {order_id}")
        return jsonify({"message": "Checkout successful", "order_id": order_id, "total_price": total_price}), 200
    except Error as e:
        logger.error(f"Database error during checkout for user {current_user}: {str(e)}")
        return jsonify({"message": "An error occurred during checkout"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)