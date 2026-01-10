# Image de base Python
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ ./src/
COPY models/ ./models/
COPY mlflow.db ./mlflow.db

# Exposer le port de l'API
EXPOSE 8000

# Variable d'environnement pour MLflow
ENV MLFLOW_TRACKING_URI=sqlite:///mlflow.db

# Commande de démarrage
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
