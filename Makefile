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

run-publisher:
	poetry run python run_pipeline.py --step publish --listing_type rent
	poetry run python run_pipeline.py --step publish --listing_type sale

run-pipeline:
	make run-scraper
	make run-publisher

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
