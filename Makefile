VENV := $(shell poetry env info --path)
SHELL := /bin/bash

# Basic development commands
install:
	poetry install

add:
	poetry add $(filter-out $@,$(MAKECMDGOALS))

dev-add:
	poetry add --group dev $(filter-out $@,$(MAKECMDGOALS))

# Host scraper execution
run-scraper:
	./run_scraper.sh

run-scraper-rent:
	./run_scraper.sh rent

run-scraper-sale:
	./run_scraper.sh sale

# Trigger Airflow DAG directly
trigger-dag-rent:
	poetry run python run_pipeline.py --step trigger-dag --rent-path $(RENT_PATH)

trigger-dag-sale:
	poetry run python run_pipeline.py --step trigger-dag --sale-path $(SALE_PATH)

trigger-dag-both:
	poetry run python run_pipeline.py --step trigger-dag --rent-path $(RENT_PATH) --sale-path $(SALE_PATH)

# Local pipeline execution commands - for testing individual components
run-api:
	poetry run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

run-cleaner:
	poetry run python run_pipeline.py --step clean --listing_type rent
	poetry run python run_pipeline.py --step clean --listing_type sale

run-publisher-api:
	poetry run python run_pipeline.py --step publish_api --listing_type rent
	poetry run python run_pipeline.py --step publish_api --listing_type sale

# This publisher-s3 step is no longer needed as S3 upload is now part of the scraper
# It's kept commented for reference
# run-publisher-s3:
# 	poetry run python run_pipeline.py --step publish_s3 --listing_type rent
# 	poetry run python run_pipeline.py --step publish_s3 --listing_type sale

# Database migrations
run-auto:
	docker compose run --rm api alembic revision --autogenerate -m "Initial schema"

run-upgrade:
	docker compose run --rm api alembic upgrade head

# Docker commands for ALL services
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

# Code quality commands
format:
	poetry run black .
	poetry run ruff check . --fix

lint:
	poetry run ruff check .

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

precommit:
	poetry run pre-commit install
	poetry run pre-commit run --all-files

# Direct Airflow commands
trigger-dag:
	docker compose exec airflow_scheduler airflow dags trigger real_estate_data_pipeline

test-dag:
	docker compose exec airflow_scheduler airflow dags trigger test_dag

list-dags:
	docker compose exec airflow_scheduler airflow dags list

pause-dag:
	docker compose exec airflow_scheduler airflow dags pause real_estate_data_pipeline

unpause-dag:
	docker compose exec airflow_scheduler airflow dags unpause real_estate_data_pipeline

unpause-test-dag:
	docker compose exec airflow_scheduler airflow dags unpause test_dag

# View Airflow logs
airflow-logs:
	docker compose exec airflow_scheduler ls -la /opt/airflow/logs

# View pipeline logs
view-pipeline-logs:
	docker compose exec airflow_scheduler bash -c 'find /opt/airflow/logs -name "*.log" | xargs cat'

# S3 utilities
s3-list:
	aws s3 ls s3://${S3_BUCKET}/raw/ --human-readable

s3-latest:
	aws s3 ls s3://${S3_BUCKET}/raw/ --human-readable | sort | tail -n 5