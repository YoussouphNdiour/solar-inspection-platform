FROM python:3.12-slim

WORKDIR /app

# Dépendances système (pour asyncpg + geoalchemy2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Sur Render : PORT est injecté automatiquement
ENV PORT=8000

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
