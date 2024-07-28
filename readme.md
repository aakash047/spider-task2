# E-commerce Microservices System

This project is an E-commerce system built using a microservices architecture. It consists of three main services: User service, Product service, and Cart service.

## Local Setup

### Prerequisites

- Docker
- Docker Compose
- Git

## Initial setup for development

python -m venv ecommerce_env
source ecommerce_env/bin/activate

pip install flask flask-jwt-extended mysql-connector-python requests pytest

mysql -u root -p
CREATE DATABASE ecommerce_users;
CREATE DATABASE ecommerce_products;
CREATE DATABASE ecommerce_carts;

create files inside their directory and create requirements.txt file too

### Steps to Run Locally

1. Clone the repository:
https://github.com/aakash047/spider-task2


2. Build and run the Docker containers:
docker-compose up --build

3. The services should now be running and accessible at:
- User service: http://localhost:8081
- Product service: http://localhost:8082
- Cart service: http://localhost:8083

## CI/CD Pipeline

This project uses GitHub Actions for CI/CD. The pipeline is configured to run on every push to the main branch.

### Pipeline Configuration

1. The pipeline is defined in `.github/workflows/main.yml`.
2. It performs the following steps:
- Checks out the code
- Builds Docker images for each microservice
- Pushes the images to Docker Hub
- Deploys the application using the deployment script

### Configuring the Pipeline

To use the CI/CD pipeline:

1. Set up the following secrets in your GitHub repository:
- DOCKERHUB_USERNAME: Your Docker Hub username
- DOCKERHUB_TOKEN: Your Docker Hub access token

2. Update the Docker Hub repository names in the GitHub Actions workflow file if necessary.

## Deployment

The deployment process is automated using a bash script (`deploy.sh`).

### Deployment Process

1. The latest Docker images are pulled from Docker Hub.
2. Existing containers are stopped and removed.
3. New containers are started using the updated images.
4. The script checks if all services are running correctly.

### Additional Setup for Deployment

1. Ensure the deployment server has Docker and Docker Compose installed.
2. Copy the `docker-compose.yml` and `deploy.sh` files to the deployment server.
3. Make the deploy script executable: `chmod +x deploy.sh`
4. Run the deployment script: `./deploy.sh`

### Accessing the Services

With the Nginx reverse proxy in place, all services can be accessed through a single port (80). The base URL for accessing the services is now:

http://localhost

For example:
- To access the User Service: http://localhost/api/users
- To access the Product Service: http://localhost/api/products
- To access the Cart Service: http://localhost/api/cart

Note: While the individual services are running on ports 5001, 5002, and 5003 respectively, they are not directly exposed to the host. All external access should go through the Nginx reverse proxy on port 80.

## Troubleshooting

- If a service fails to start, you can check its logs using `docker-compose logs [service_name]`.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
