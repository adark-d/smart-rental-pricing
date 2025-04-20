FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libpq-dev \
    cmake \
    curl \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry config installer.max-workers 1 && \
    poetry install --no-interaction --no-ansi --no-root

ENV PIP_DEFAULT_TIMEOUT=100

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
