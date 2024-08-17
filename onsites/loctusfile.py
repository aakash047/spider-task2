from locust import HttpUser, TaskSet, task, between
import logging
import json

class UserServiceBehavior(TaskSet):
    @task(1)
    def register(self):
        response = self.client.post("/register", json={
            "username": "testuser",
            "password": "testpass",
            "email": "test@example.com"
        })
        logging.info(f"Register response: {response.status_code}, {response.text}")
        if response.status_code != 200:
            logging.error(f"Register failed: {response.status_code}, {response.text}")

    @task(2)
    def login(self):
        response = self.client.post("/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        logging.info(f"Login response: {response.status_code}, {response.text}")
        if response.status_code != 200:
            logging.error(f"Login failed: {response.status_code}, {response.text}")
        else:
            # Assuming the token is in the response, save it for later use
            self.user.token = json.loads(response.text).get('access_token')
            logging.info(f"Token saved: {self.user.token}")

class ProductServiceBehavior(TaskSet):
    @task(1)
    def add_product(self):
        response = self.client.post("/products", json={
            "name": "Test Product",
            "description": "This is a test product",
            "price": 10.99,
            "stock": 100
        })
        logging.info(f"Add product response: {response.status_code}, {response.text}")
        if response.status_code != 200:
            logging.error(f"Add product failed: {response.status_code}, {response.text}")

    @task(2)
    def get_product(self):
        response = self.client.get("/products/1")
        logging.info(f"Get product response: {response.status_code}, {response.text}")
        if response.status_code != 200:
            logging.error(f"Get product failed: {response.status_code}, {response.text}")

    @task(1)
    def update_product(self):
        response = self.client.put("/products/1", json={
            "name": "Updated Product",
            "description": "This is an updated test product",
            "price": 15.99,
            "stock": 50
        })
        logging.info(f"Update product response: {response.status_code}, {response.text}")
        if response.status_code != 200:
            logging.error(f"Update product failed: {response.status_code}, {response.text}")

    @task(1)
    def delete_product(self):
        response = self.client.delete("/products/1")
        logging.info(f"Delete product response: {response.status_code}, {response.text}")
        if response.status_code != 200:
            logging.error(f"Delete product failed: {response.status_code}, {response.text}")

class CartServiceBehavior(TaskSet):
    @task(1)
    def add_to_cart(self):
        if not hasattr(self.user, 'token'):
            logging.error("No token available for cart operation")
            return
        response = self.client.post("/cart/add", json={
            "product_id": 2,
            "quantity": 2
        }, headers={
            "Authorization": f"Bearer {self.user.token}"
        })
        logging.info(f"Add to cart response: {response.status_code}, {response.text}")
        if response.status_code != 200:
            logging.error(f"Add to cart failed: {response.status_code}, {response.text}")

class UserServiceUser(HttpUser):
    host = "http://172.24.0.3:5001"  # Update this to the correct IP and port
    tasks = [UserServiceBehavior]
    wait_time = between(1, 5)

class ProductServiceUser(HttpUser):
    host = "http://172.23.0.5:5002"  # Confirm this is correct
    tasks = [ProductServiceBehavior]
    wait_time = between(1, 5)

class CartServiceUser(HttpUser):
    host = "http://172.23.0.5:5003"  # Confirm this is correct
    tasks = [CartServiceBehavior]
    wait_time = between(1, 5)