"""
A simple test DAG to verify Airflow is working properly and test connections
"""

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    "test_dag",
    schedule_interval=None,
    start_date=datetime(2025, 4, 24),
    catchup=False,
    tags=["test"],
) as dag:

    task1 = BashOperator(task_id="print_date", bash_command="date")

    task2 = BashOperator(
        task_id="print_hello", bash_command='echo "Hello from Airflow!"'
    )

    # Test PostgreSQL connection
    test_db = BashOperator(
        task_id="test_postgres_connection",
        bash_command="""
            PGPASSWORD=${POSTGRES_PASSWORD} \
            psql -h ${POSTGRES_HOST} \
                 -p ${POSTGRES_PORT} \
                 -U ${POSTGRES_USER} \
                 -d ${POSTGRES_DB} \
                 -c "SELECT 1 as connected"
        """,
    )

    # Test API connection
    test_api = BashOperator(
        task_id="test_api_connection",
        bash_command='curl -s -L http://${API_HOST}:${API_PORT}/api/v1/health/ | grep "status"',
    )

    # Test run_pipeline.py script exists
    test_pipeline = BashOperator(
        task_id="test_pipeline_script",
        bash_command="cd /opt/airflow && ls -la run_pipeline.py",
    )

    # Define task dependencies
    task1 >> task2 >> [test_db, test_api, test_pipeline]
