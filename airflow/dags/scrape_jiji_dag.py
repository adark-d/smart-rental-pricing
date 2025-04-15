import subprocess
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def run_scraper():
    subprocess.run(["python", "scraper/jiji_scraper.py"], check=True)


with DAG(
    dag_id="scrape_jiji_daily",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["scraper", "jiji"],
) as dag:

    scrape_task = PythonOperator(
        task_id="scrape_jiji",
        python_callable=run_scraper,
    )

    scrape_task
