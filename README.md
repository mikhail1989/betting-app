# Betting App and Provider App

This repository contains two applications: a Betting App and a Provider App. The Betting App allows users to place bets on events, while the Provider App serves as a data source for the Betting App, providing active events and related information.

## Technologies

- **FastAPI**
- **RabbitMQ**
- **Redis**
- **Docker**
- **Docker Compose**
- **PostgreSQL**
- **SQLAlchemy**

## Requirements

Make sure you have the following installed:

- Docker
- Docker Compose

## Run the Applications

To start the applications, follow these steps:

  Start the Provider App Container First:
  
    docker-compose up -d provider
  
  Then Start the Betting App Container:
  
    docker-compose up -d betting
    
  To stop the containers:
  
    docker-compose down
