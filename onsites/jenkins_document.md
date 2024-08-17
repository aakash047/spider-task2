# DevOps Project: CI/CD Pipeline with Jenkins, Docker, and AWS

## Project Overview
This project implements a CI/CD pipeline using Jenkins, Docker, and AWS EC2. It includes rate limiting and load balancing with Nginx, uses Ansible for Docker setup on EC2 instances, and incorporates load testing with Locust.

## Initial Challenges
Encountered difficulties installing Jenkins on a MacBook Air M1 due to Docker group permissions and compatibility issues with the jenkinsci/blueocean image on ARM architecture.

## Solution: AWS EC2
To circumvent these challenges, the project was migrated to an AWS EC2 instance.

## Implementation Steps
* Set up an EC2 instance.
* Installed Jenkins and Docker on the EC2 instance.
* Configured Git integration within Jenkins.
* Created a Jenkins CI/CD pipeline.
* Implemented rate limiting and load balancing in Nginx.
* Utilized Ansible for Docker setup on EC2 instances.
* Integrated load testing with Locust.

## Key Resources
* Jenkins LTS for macOS
* Jenkins Pipeline Example
* Jenkins-GitHub Integration Guide
* Nginx Rate Limiting Guide
* Locust Documentation

## Troubleshooting
* Addressed Docker-related issues on macOS.
* Implemented load testing using Locust.
