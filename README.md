# 🌍 Air Quality NO2 Prediction - MLOps Project

[![CI/CD Pipeline](https://github.com/manartrimeche/MLOp-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/manartrimeche/MLOp-Project/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688)](https://fastapi.tiangolo.com/)
[![MLflow](https://img.shields.io/badge/MLflow-2.9.0-0194E2)](https://mlflow.org/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> Projet MLOps pour prédire la concentration de dioxyde d'azote (NO2) dans l'air à partir de mesures environnementales et d'indicateurs de qualité de l'air.

## 1. Vue d'ensemble

Ce dépôt met en place une chaîne d'apprentissage automatique complète avec :

- préparation et nettoyage des données,
- entraînement d'un modèle de régression,
- journalisation avec MLflow,
- versioning des données avec DVC,
- exposition d'un service API REST via FastAPI,
- conteneurisation avec Docker,
- automatisation CI/CD via GitHub Actions.

Le projet cible la prédiction de la variable `NO2(GT)` à partir d'un ensemble de capteurs et variables environnementales.

## 2. Objectif métier

L'objectif est de fournir un modèle fiable capable d'estimer la concentration de NO2 dans l'air afin de :

- monitorer la qualité de l'air,
- aider à la prise de décision environnementale,
- servir de base à un système de détection ou d'alerte,
- démontrer une architecture MLOps reproductible et scalable.

## 3. Stack technique

- Python 3.11
- FastAPI
- Uvicorn
- MLflow
- scikit-learn
- pandas / numpy
- Docker / Docker Compose
- GitHub Actions
- DVC
- Pytest

## 4. Architecture du projet

```text
MLOp-Project/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
├── .dvc/
├── api/
│   └── main.py
├── data/
│   └── prédiction_de_la_qualité_de_air.csv.dvc
├── docs/
│   └── api_guide.md
├── models/
│   ├── feature_names.json
│   └── random_forest_no2_model.pkl
├── notebooks/
│   └── exploratory_analysis.ipynb
├── scripts/
│   ├── check_model_features.py
│   └── setup_environment.ps1
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── data_prep.py
│   ├── train.py
│   └── promote_best_model.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_data_prep.py
│   └── test_train.py
├── .dockerignore
├── .dvcignore
├── .env.example
├── .gitignore
├── Dockerfile
├── Dockerfile.mlflow
├── LICENSE
├── README.md
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
└── mlflow.db
```

## 5. Modèle et performances

Le projet entraîne un modèle de régression : `RandomForestRegressor`.

Métriques observées :

- Modèle : Random Forest Regressor
- MAE : 9.05 µg/m³
- RMSE : 14.46 µg/m³
- R² : 0.9862

Ces résultats indiquent une bonne précision pour la prédiction de la concentration de NO2.

## 6. Installation

### Prérequis

- Python 3.11+
- pip
- Docker et Docker Compose (optionnel)
- Git

### 1) Cloner le dépôt

```bash
git clone https://github.com/manartrimeche/MLOp-Project.git
cd MLOp-Project
```

### 2) Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# ou
.venv\Scripts\activate      # Windows PowerShell
```

### 3) Installer les dépendances

```bash
pip install -r requirements.txt
```

Pour les outils de développement :

```bash
pip install -r requirements-dev.txt
```

## 7. Variables d'environnement

Un fichier `.env.example` est fourni.

```env
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
MLFLOW_EXPERIMENT_NAME=air-quality-no2-prediction
API_HOST=0.0.0.0
API_PORT=8000
MODEL_ALIAS=champion
```

Pour l'utiliser :

```bash
cp .env.example .env
```

## 8. Entraînement du modèle

Le script principal pour l'entraînement est :

```bash
python src/train.py
```

### Ce que fait l'entraînement

- charge les données depuis `data/`,
- nettoie et prépare les features,
- divise les données en train/test,
- entraîne plusieurs variantes de Random Forest,
- calcule MAE, RMSE, R²,
- enregistre le modèle localement dans `models/`,
- enregistre les features dans `models/feature_names.json`,
- journalise le modèle dans MLflow.

## 9. Lancement local de l'API

### Option 1 : avec Python direct

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

Ensuite ouvrez :

- Swagger UI : `http://localhost:8000/docs`
- Health check : `http://localhost:8000/health`

### Option 2 : via Docker Compose

```bash
docker-compose up --build
```

L'API sera disponible sur :

```text
http://localhost:8000
```

## 10. Endpoints API

### GET `/`
Retourne des informations générales sur l'API.

### GET `/health`
Vérifie que le service est bien démarré et que le modèle est chargé.

### POST `/predict`
Prédit une valeur pour un seul échantillon.

Exemple JSON :

```json
{
  "CO(GT)": 2.6,
  "PT08.S1(CO)": 1360.0,
  "NMHC(GT)": 150.0,
  "C6H6(GT)": 11.9,
  "PT08.S2(NMHC)": 1046.0,
  "NOx(GT)": 113.0,
  "PT08.S3(NOx)": 166.0,
  "PT08.S4(NO2)": 1056.0,
  "PT08.S5(O3)": 1692.0,
  "T": 13.6,
  "RH": 48.9,
  "AH": 0.7578
}
```

Réponse attendue :

```json
{
  "prediction": 42.75,
  "model_version": "champion (v1)"
}
```

### POST `/predict/batch`
Prédit plusieurs échantillons en une seule requête.

Exemple curl :

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "CO(GT)": 2.6,
    "PT08.S1(CO)": 1360.0,
    "NMHC(GT)": 150.0,
    "C6H6(GT)": 11.9,
    "PT08.S2(NMHC)": 1046.0,
    "NOx(GT)": 113.0,
    "PT08.S3(NOx)": 166.0,
    "PT08.S4(NO2)": 1056.0,
    "PT08.S5(O3)": 1692.0,
    "T": 13.6,
    "RH": 48.9,
    "AH": 0.7578
  }'
```

## 11. MLflow

MLflow est utilisé pour :

- enregistrer les expériences d'entraînement,
- logger paramètres et métriques,
- versionner les modèles,
- gérer les aliases comme `champion`.

Pour démarrer MLflow localement :

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --host 0.0.0.0 --port 5000
```

Ensuite ouvrez :

```text
http://localhost:5000
```

## 12. Tests

La suite de tests est située dans le dossier `tests/`.

Exécution :

```bash
pytest
```

Les tests vérifient notamment :

- la préparation des données,
- la logique d'entraînement du modèle,
- les réponses de l'API.

## 13. DVC

Le dépôt utilise DVC pour le versioning des données lourdes.

Exemple :

```bash
dvc status
dvc pull
```

Cela permet de gérer les jeux de données de manière reproductible sans les stocker directement dans le dépôt Git.

## 14. CI/CD

Le dépôt contient des workflows GitHub Actions :

- `ci.yml` pour l'intégration continue,
- `release.yml` pour la publication / délivrance.

Le pipeline automatise typiquement :

- installation des dépendances,
- exécution des tests,
- contrôle de qualité,
- validation de la construction Docker.

## 15. Bonnes pratiques MLOps mises en œuvre

- séparation claire entre données, code et modèles,
- traçabilité des expériences via MLflow,
- structure de projet modulaire,
- API exposée pour inférence en production,
- conteneurisation du service,
- versioning du dataset et des artefacts,
- automatisation des validations via CI.

## 16. Roadmap possible

- ajouter une surveillance des métriques de production,
- mettre en place un système de régression continue,
- sécuriser les endpoints API,
- ajouter un dashboard de monitoring,
- déployer sur un service cloud (Azure, AWS, GCP, Render, Railway, etc.),
- améliorer la robustesse du pipeline de données.

## 17. Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE).

## 18. Contributeurs

- [manartrimeche](https://github.com/manartrimeche)

## 19. Contact

Pour toute question ou contribution, ouvrez une issue sur le dépôt GitHub ou contactez le propriétaire du projet.

---

Merci d'avoir visité ce projet. Si vous souhaitez, je peux aussi vous proposer :

- une version README plus courte et plus élégante,
- une version en anglais,
- une version orientée portfolio / démonstration,
- ou une version adaptée à un projet de stage ou de candidature.
