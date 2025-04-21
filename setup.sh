#!/bin/bash

# === SETUP SCRIPT FOR SMART RENTAL PRICING PROJECT ===
# This script installs dependencies, runs Docker Compose, and prepares the API.

# Install Poetry
echo "Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -

# Add to path (if needed)
export PATH="$HOME/.local/bin:$PATH"

# Install Dependencies
echo "Installing Python packages via Poetry..."
poetry install

# Build Docker Containers
echo "Building Docker containers..."
docker compose build

# Start API and DB
echo "Starting services..."
docker compose up -d

# Run Alembic Migrations
echo "Running Alembic migrations..."
docker compose exec api poetry run alembic upgrade head

# Show API URL
echo "Visit your API docs at: http://localhost:8000/docs"
