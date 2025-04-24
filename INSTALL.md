# Installation Guide

This document provides detailed instructions for setting up the Smart Rental Pricing project.

## Prerequisites

- Docker and Docker Compose (latest version recommended)
- Python 3.11+
- Poetry (for local development)
- Git

## Initial Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd smart-rental-pricing
   ```

2. Create a `.env` file based on the example:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file to set your specific configuration values.

3. Create required directories:
   ```bash
   mkdir -p data/raw/rent data/raw/sale \
            data/cleaned/rent data/cleaned/sale \
            data/failed \
            data/compressed \
            logs
   ```

## Docker Setup

1. Build the Docker images:
   ```bash
   make build
   ```

2. Start all services:
   ```bash
   make up
   ```

3. Run database migrations:
   ```bash
   make run-upgrade
   ```

4. Verify that services are running:
   ```bash
   make ps
   ```

## Testing the Setup

1. List available Airflow DAGs:
   ```bash
   make list-dags
   ```

2. Unpause and trigger the test DAG:
   ```bash
   make unpause-test-dag
   make test-dag
   ```

3. Check the Airflow UI at http://localhost:8080 to see if the test DAG ran successfully.

4. If the test passed, you can unpause and trigger the main pipeline:
   ```bash
   make unpause-dag
   make trigger-dag
   ```

## Local Development Setup (Optional)

If you want to develop without Docker:

1. Install dependencies using Poetry:
   ```bash
   make install
   ```

2. Set up a PostgreSQL database and update the `.env` file.

3. Run database migrations:
   ```bash
   poetry run alembic upgrade head
   ```

4. Start the API:
   ```bash
   make run-api
   ```

5. Run the pipeline manually:
   ```bash
   make run-pipeline
   ```

## Troubleshooting

- If you encounter permission issues with data directories, ensure they have the correct permissions:
  ```bash
  chmod -R 777 data logs
  ```

- If container communication fails, ensure they're on the same network:
  ```bash
  docker network inspect rental_pricing_network
  ```

- For Airflow-specific issues, check the logs:
  ```bash
  docker logs airflow_webserver
  docker logs airflow_scheduler
  ```