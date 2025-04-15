FROM python:3.12-slim

WORKDIR /app

COPY ./dashboard /app/dashboard
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
