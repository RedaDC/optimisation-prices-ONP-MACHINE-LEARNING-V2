# Utiliser une image Python officielle légère
FROM python:3.9-slim

# Définir le répertoire de travail dans le container
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le contenu du projet dans le container
COPY . .

# Exposer le port par défaut de Streamlit
EXPOSE 8501

# Commande pour lancer l'application au démarrage du container
ENTRYPOINT ["streamlit", "run", "app_premium.py", "--server.port=8501", "--server.address=0.0.0.0"]
