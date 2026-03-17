FROM python:3.12-slim

WORKDIR /app

# Dépendances système (asyncpg + geoalchemy2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY src/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code backend
COPY src/backend/ .

# Copier le dossier shared (anomalies, rapports) pour le dev local
COPY shared/ ./shared/

# Render injecte $PORT automatiquement (défaut 10000)
ENV PORT=10000

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
