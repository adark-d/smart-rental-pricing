FROM apache/airflow:2.8.0-python3.11

USER root

# --- System dependencies & Chromium ---
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    xdg-utils \
    curl \
    wget \
    unzip

RUN ln -s /usr/bin/chromium /usr/bin/google-chrome

# Switch to airflow
USER airflow
WORKDIR ${AIRFLOW_HOME}

# Install Poetry and dependencies
RUN pip install --user poetry

ENV PATH="${PATH}:/home/airflow/.local/bin"

# Set fixed Poetry virtualenv path
RUN poetry config virtualenvs.create true && \
    poetry config virtualenvs.path /opt/airflow/.venv

# Install dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --no-interaction

# Copy code and DAGs
COPY run_pipeline.py ./run_pipeline.py
COPY src ./src
COPY configs ./configs
COPY airflow/dags ./dags
COPY airflow/plugins ./plugins
COPY .env .env
