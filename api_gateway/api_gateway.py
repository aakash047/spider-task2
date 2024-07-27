# api_gateway.py
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import requests

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

USER_SERVICE_URL = 'http://user-service:5001'
PRODUCT_SERVICE_URL = 'http://product-service:5002'
CART_SERVICE_URL = 'http://cart-service:5003'

@app.route('/api/register', methods=['POST'])
def register():
    response = requests.post(f"{USER_SERVICE_URL}/register", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/api/login', methods=['POST'])
def login():
    response = requests.post(f"{USER_SERVICE_URL}/login", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/api/products', methods=['GET'])
def get_products():
    response = requests.get(f"{PRODUCT_SERVICE_URL}/products")
    return jsonify(response.json()), response.status_code

@app.route('/api/cart', methods=['GET'])
@jwt_required()
def get_cart():
    current_user = get_jwt_identity()
    headers = {'Authorization': request.headers.get('Authorization')}
    response = requests.get(f"{CART_SERVICE_URL}/cart", headers=headers)
    return jsonify(response.json()), response.status_code

# Implement other routes for remaining endpoints

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)