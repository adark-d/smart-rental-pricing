# ----------- VARIABLES -----------

# Docker Compose project name (optional)
PROJECT_NAME=smart-rental-pricing

# Profile for migration-only container
MIGRATE_SERVICE=smart_rental_migrate

# ----------- COMMANDS -----------

# Start all core services (db, redis, api)
up:
	docker compose up -d

# Stop and remove all services and volumes
down:
	docker compose down -v --remove-orphans

# Build containers
build:
	docker compose build

# Show logs for API
logs:
	docker compose logs -f api

# Show status of containers
ps:
	docker compose ps

# Prune all stopped containers (optional cleanup)
clean:
	docker container prune -f
	docker network prune -f

revision:
	@read -p "Enter migration message: " msg; \
	docker compose run --rm api poetry run alembic revision --autogenerate -m "$$msg"

upgrade:
	@echo "Running Alembic upgrade..."
	docker compose run --rm api poetry run alembic upgrade head

old-run: down clean build up upgrade
new-run: down clean build up revision upgrade