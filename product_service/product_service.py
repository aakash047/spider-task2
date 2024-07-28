# product_service.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from common.logging_config import setup_logger

app = Flask(__name__)
logger = setup_logger('product_service')

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

@app.route('/products', methods=['GET'])
def get_products():
    logger.info("Fetching all products")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        logger.info(f"Successfully fetched {len(products)} products")
        return jsonify(products), 200
    except Error as e:
        logger.error(f"Database error while fetching products: {str(e)}")
        return jsonify({"message": f"An error occurred while fetching products: {str(e)}"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    logger.info(f"Fetching product with id: {product_id}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        if product:
            logger.info(f"Successfully fetched product: {product_id}")
            return jsonify(product), 200
        else:
            logger.warning(f"Product not found: {product_id}")
            return jsonify({"message": "Product not found"}), 404
    except Error as e:
        logger.error(f"Database error while fetching product {product_id}: {str(e)}")
        return jsonify({"message": "An error occurred while fetching the product"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock')

    if not name or not price or stock is None:
        logger.warning(f"Attempt to add product with missing fields: {data}")
        return jsonify({"message": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, description, price, stock) VALUES (%s, %s, %s, %s)",
                       (name, description, price, stock))
        conn.commit()
        logger.info(f"Product added successfully: {name}")
        return jsonify({"message": "Product added successfully", "id": cursor.lastrowid}), 201
    except Error as e:
        logger.error(f"Database error while adding product: {str(e)}")
        return jsonify({"message": "An error occurred while adding the product"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock')

    logger.info(f"Updating product: {product_id}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET name = %s, description = %s, price = %s, stock = %s WHERE id = %s",
                       (name, description, price, stock, product_id))
        conn.commit()
        if cursor.rowcount > 0:
            logger.info(f"Product updated successfully: {product_id}")
            return jsonify({"message": "Product updated successfully"}), 200
        else:
            logger.warning(f"Product not found for update: {product_id}")
            return jsonify({"message": "Product not found"}), 404
    except Error as e:
        logger.error(f"Database error while updating product {product_id}: {str(e)}")
        return jsonify({"message": "An error occurred while updating the product"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    logger.info(f"Deleting product: {product_id}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        if cursor.rowcount > 0:
            logger.info(f"Product deleted successfully: {product_id}")
            return jsonify({"message": "Product deleted successfully"}), 200
        else:
            logger.warning(f"Product not found for deletion: {product_id}")
            return jsonify({"message": "Product not found"}), 404
    except Error as e:
        logger.error(f"Database error while deleting product {product_id}: {str(e)}")
        return jsonify({"message": "An error occurred while deleting the product"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)