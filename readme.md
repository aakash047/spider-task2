python -m venv ecommerce_env
source ecommerce_env/bin/activate

pip install flask flask-jwt-extended mysql-connector-python requests pytest

mysql -u root -p
CREATE DATABASE ecommerce_users;
CREATE DATABASE ecommerce_products;
CREATE DATABASE ecommerce_carts;

create files inside their directory and create requirements.txt file too


