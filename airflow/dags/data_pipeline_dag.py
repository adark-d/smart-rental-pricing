from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator
from airflow.utils.task_group import TaskGroup

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# Define potential listing types
listing_types = ["rent", "sale"]

with DAG(
    dag_id="real_estate_data_pipeline",
    default_args=default_args,
    description="Process real estate data from S3, clean it, and publish it",
    schedule_interval=None,  # Only triggered externally by the scraper
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["real_estate", "ETL"],
    max_active_runs=1,
) as dag:

    # Check database connectivity
    wait_for_db = BashOperator(
        task_id="wait_for_postgres",
        bash_command="""
        PGPASSWORD=${POSTGRES_PASSWORD} \
        psql -h ${POSTGRES_HOST} \
             -p ${POSTGRES_PORT} \
             -U ${POSTGRES_USER} \
             -d ${POSTGRES_DB} \
             -c "SELECT 1 as connected"
        """,
    )

    # Create placeholders for task group references
    task_group_refs = {}

    # Function to determine which listing types to process
    def determine_listing_types(**context):
        """
        Check which listing types are available in the DAG run configuration
        and return the first task ID in each pipeline to execute
        """
        try:
            s3_paths = context["dag_run"].conf.get("s3_paths", {})
            available_types = list(s3_paths.keys())

            if not available_types:
                # If no types are available, execute a dummy task
                return "no_data_found"

            # For branching, we need to return specific task IDs (not task group IDs)
            result = []
            for lt in available_types:
                if lt in listing_types:
                    # Return the first task in each pipeline group
                    result.append(f"{lt}_pipeline.download")

            return result if result else "no_data_found"

        except Exception as e:
            print(f"Error determining listing types: {e}")
            return "no_data_found"

    # Branching task to decide which listing types to process
    branch_task = BranchPythonOperator(
        task_id="determine_listing_types",
        python_callable=determine_listing_types,
        # provide_context is deprecated in Airflow 2.2+, context is provided by default
    )

    # Task to handle case where no data is found
    no_data_task = BashOperator(
        task_id="no_data_found",
        bash_command='echo "No listing data found in DAG run configuration"',
    )

    # Process each listing type
    for lt in listing_types:
        with TaskGroup(group_id=f"{lt}_pipeline") as tg:

            # Download the data from S3
            download = BashOperator(
                task_id="download",
                bash_command=f"""
                # Ensure directory exists
                mkdir -p /opt/airflow/data/raw/
                
                # Get S3 path from DAG run configuration
                S3_PATH="{{{{ dag_run.conf['s3_paths']['{lt}'] }}}}"
                
                # Extract bucket and key
                BUCKET=$(echo $S3_PATH | cut -d'/' -f3)
                KEY=$(echo $S3_PATH | cut -d'/' -f4-)
                
                # Use awscli to download
                aws s3 cp "s3://$BUCKET/$KEY" "/opt/airflow/data/raw/latest_{lt}.json"
                
                echo "Downloaded {lt} data to /opt/airflow/data/raw/latest_{lt}.json"
                """,
            )

            # Clean the data
            clean = BashOperator(
                task_id="clean",
                bash_command=f"""
                cd /opt/airflow && \
                export PYTHONPATH="/opt/airflow:/home/airflow/.local/lib/python3.11/site-packages: \
                $PYTHONPATH" && \
                python run_pipeline.py --step clean --listing_type {lt}
                """,
            )

            # Publish to API endpoint
            publish_api = BashOperator(
                task_id="publish_api",
                bash_command=f"""
                cd /opt/airflow && \
                export PYTHONPATH="/opt/airflow:/home/airflow/.local/lib/python3.11/site-packages: \
                $PYTHONPATH" && \
                python run_pipeline.py --step publish_api --listing_type {lt}
                """,
            )

            # Set task dependencies within the group
            download >> clean >> publish_api

        # Connect the branch task to the first task in this group
        # This connection is handled by the BranchPythonOperator return value
        # We don't need an explicit connection here

    # Set the overall workflow
    wait_for_db >> branch_task >> no_data_task

    # Branch task connections are handled automatically by the task's return value
    # We don't need to explicitly set them here
