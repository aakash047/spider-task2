#!/bin/bash

set -e

echo "Pulling the latest images..."
docker-compose pull

echo "Restarting the services..."
docker-compose up -d

echo "Deployment completed successfully."
