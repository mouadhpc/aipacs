FROM python:3.11-slim

# Métadonnées
LABEL maintainer="AI PACS Team"
LABEL description="Application IA pour Radiologie avec PACS Interne"
LABEL version="1.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    dcmtk \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR $APP_HOME

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY src/ ./src/
COPY config/ ./config/

# Création d'un utilisateur non-root
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser $APP_HOME
USER appuser

# Exposition du port
EXPOSE 8000

# Point d'entrée
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]