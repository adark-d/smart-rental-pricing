VENV := $(shell poetry env info --path)

install:
	poetry install

add:
	poetry add $(filter-out $@,$(MAKECMDGOALS))

dev-add:
	poetry add --group dev $(filter-out $@,$(MAKECMDGOALS))

run-api:
	poetry run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

run-scraper:
	caffeinate -i poetry run python run_pipeline.py --step scrape --listing_type rent
	caffeinate -i poetry run python run_pipeline.py --step scrape --listing_type sale

run-cleaner:
	poetry run python run_pipeline.py --step clean --listing_type rent
	poetry run python run_pipeline.py --step clean --listing_type sale

run-publisher-api:
	poetry run python run_pipeline.py --step publish_api --listing_type rent
	poetry run python run_pipeline.py --step publish_api --listing_type sale

run-publisher-s3:
	poetry run python run_pipeline.py --step publish_s3 --listing_type rent
	poetry run python run_pipeline.py --step publish_s3 --listing_type sale

run-pipeline:
	make run-scraper
	make run-cleaner
	make run-publisher-api
	make run-publisher-s3
	

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
