VENV := $(shell poetry env info --path)

install:
	poetry install

add:
	poetry add $(filter-out $@,$(MAKECMDGOALS))

dev-add:
	poetry add --group dev $(filter-out $@,$(MAKECMDGOALS))

run-api:
	poetry run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

run-dashboard:
	poetry run streamlit run dashboard/app.py

run-scraper:
	poetry run python scraper/jiji_scraper.py

train-model:
	poetry run python src/model/train.py

monitor:
	poetry run python monitoring/run_monitoring.py

format:
	poetry run black .
	poetry run ruff check . --fix

lint:
	poetry run ruff check .

test:
	poetry run pytest tests/

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

precommit:
	poetry run pre-commit install
	poetry run pre-commit run --all-files
