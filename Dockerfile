FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && \
    poetry config installer.max-workers 1 && \
    poetry install --no-interaction --no-ansi --no-root --only main

ENV PIP_DEFAULT_TIMEOUT=100

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
COPY configs ./configs
COPY src ./src

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]