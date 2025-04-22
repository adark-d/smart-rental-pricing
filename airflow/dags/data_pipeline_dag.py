from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

listing_types = ["rent", "sale"]
POETRY_ENV_PATH = "/opt/airflow/.venv"
PYTHON_BIN = f"{POETRY_ENV_PATH}/bin/python"

base_command = f"{PYTHON_BIN} run_pipeline.py"

with DAG(
    dag_id="real_estate_data_pipeline",
    default_args=default_args,
    description="ETL pipeline for scraping, cleaning, and publishing real estate listings",
    schedule_interval="0 6 * * 1",  # Every Monday at 6 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["real_estate", "ETL"],
) as dag:

    for listing_type in listing_types:
        scrape = BashOperator(
            task_id=f"scrape_{listing_type}",
            bash_command=f"{base_command} --step scrape --listing_type {listing_type}",
        )

        clean = BashOperator(
            task_id=f"clean_{listing_type}",
            bash_command=f"{base_command} --step clean --listing_type {listing_type}",
        )

        publish_api = BashOperator(
            task_id=f"publish_api_{listing_type}",
            bash_command=f"{base_command} --step publish_api --listing_type {listing_type}",
        )

        publish_s3 = BashOperator(
            task_id=f"publish_s3_{listing_type}",
            bash_command=f"{base_command} --step publish_s3 --listing_type {listing_type}",
        )

        scrape >> clean >> [publish_api, publish_s3]
