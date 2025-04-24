# Base: lightweight Airflow with Python 3.11
FROM apache/airflow:slim-2.8.1-python3.11

# Switch to root for system packages
USER root

# Install PostgreSQL client, AWS CLI, and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

# Make directories accessible
RUN mkdir -p /opt/airflow/logs \
    /opt/airflow/dags \
    /opt/airflow/plugins \
    /opt/airflow/data \
    /opt/airflow/data/raw \
    /opt/airflow/data/cleaned \
    /opt/airflow/data/failed \
    /opt/airflow/data/compressed && \
    chown -R airflow:0 /opt/airflow && \
    chmod -R 775 /opt/airflow

# Switch to airflow user for pip installations
USER airflow
WORKDIR /opt/airflow

# Install all required Python dependencies for the pipeline
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    loguru==0.7.3 \
    numpy==1.26.0 \
    pandas==2.2.3 \
    plotly==5.17.0 \
    requests==2.32.3 \
    joblib==1.4.2 \
    dynaconf==3.2.10 \
    orjson==3.10.16 \
    psycopg2-binary==2.9.10 \
    boto3==1.37.37 \
    python-dotenv==1.1.0 \
    apache-airflow-providers-amazon>=8.0.0

# Set up environment variables
ENV PYTHONPATH="/opt/airflow:/opt/airflow/dags:/opt/airflow/plugins:/home/airflow/.local/lib/python3.11/site-packages:${PYTHONPATH}"
ENV PATH="/home/airflow/.local/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"