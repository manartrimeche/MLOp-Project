# 📁 Structure du Projet MLOps

## Vue d'ensemble

```
MLOp-Project/
├── src/                          # Code source principal
│   ├── __init__.py
│   ├── api.py                    # 🚀 API FastAPI avec MLflow
│   ├── train.py                  # Entraînement avec MLflow
│   ├── train_final_model.py       # Modèle final optimisé
│   ├── data_prep.py              # Préparation des données
│   ├── pipelines.py              # Pipelines ML
│   ├── optuna_optimization.py    # Hyperparameter tuning
│   └── promote_best_model.py     # Promotion de modèle
│
├── tests/                        # Tests unitaires
│   ├── __init__.py
│   ├── test_api.py              # Tests API
│   ├── test_data_prep.py        # Tests préparation
│   ├── test_train.py            # Tests entraînement
│   └── __pycache__/
│
├── data/                         # Données (DVC tracked)
│   ├── prédiction_de_la_qualité_de_air.csv
│   ├── prédiction_de_la_qualité_de_air.csv.dvc
│   ├── processed_data.csv
│   └── processed_data.csv.dvc
│
├── scripts/                      # Scripts d'utilitaire
│   ├── README.md                 # 📖 Guide des scripts
│   ├── test_api_prediction.py   # Test API complet
│   ├── promote_model_to_production.py  # Promotion modèle
│   └── check_model_features.py   # Vérification features
│
├── docs/                         # Documentation
│   ├── api_guide.md             # 📖 Guide API complet (550+ lignes)
│   └── deployment.md            # Guide déploiement
│
├── notebooks/                    # Jupyter Notebooks
│   └── exploratory_analysis.ipynb
│
├── models/                       # Modèles sauvegardés
│   ├── final_model.pkl          # Modèle final (pickle)
│   └── feature_names.json       # Noms des features
│
├── mlruns/                       # MLflow artifact store
│   ├── 2/                       # Expérience 2
│   │   └── models/
│   │       └── m-*/artifacts/   # Artifacts des modèles
│   └── 3/                       # Expérience 3 (final)
│       └── */artifacts/
│
├── htmlcov/                      # Coverage report (HTML)
│   └── index.html               # Accès: open htmlcov/index.html
│
├── .github/                      # GitHub configuration
│   └── workflows/
│       ├── ci.yml               # Pipeline CI/CD (GitHub Actions)
│       └── release.yml          # Pipeline release
│
├── .dvc/                         # Data Version Control
│   └── [DVC config]
│
├── .venv/                        # Virtual environment Python
│
├── Dockerfile                    # 🐳 Image Docker API
├── Dockerfile.mlflow             # 🐳 Image MLflow (optionnel)
├── docker-compose.yml            # 🐳 Orchestration (MLflow + API)
├── .dockerignore                 # Fichiers à exclure de l'image
│
├── .env                          # ⚙️  Configuration locale (gitignored)
├── .env.example                  # ⚙️  Exemple de configuration
├── .env.docker                   # ⚙️  Configuration Docker
│
├── .gitignore                    # Fichiers git ignorés
├── .dvcignore                    # Fichiers DVC ignorés
│
├── requirements.txt              # 📦 Dépendances production
├── requirements-dev.txt          # 📦 Dépendances dev + test
│
├── pytest.ini                    # ⚙️  Configuration pytest
├── Makefile                      # 🔧 Commandes courantes
│
├── README.md                     # 📖 Accueil du projet
├── LICENSE                       # Licence MIT
│
├── COMPLIANCE_REPORT.md          # ✅ Rapport de conformité
└── CORRECTIONS_SUMMARY.md        # 📝 Résumé des corrections

```

---

## 📋 Description des fichiers clés

### Code source (`src/`)

| Fichier | Objectif |
|---------|----------|
| `api.py` | ⭐ API FastAPI avec chargement MLflow Registry |
| `train.py` | Entraînement basique avec MLflow |
| `train_final_model.py` | Modèle final optimisé avec hyperparamètres |
| `data_prep.py` | Chargement, nettoyage, préparation des données |
| `optuna_optimization.py` | Hyperparameter tuning avec Optuna |
| `pipelines.py` | Pipelines ML personnalisés |
| `promote_best_model.py` | Promotion du meilleur modèle |

### Tests (`tests/`)

| Fichier | Couverture |
|---------|-----------|
| `test_api.py` | Endpoints FastAPI |
| `test_data_prep.py` | Préparation données |
| `test_train.py` | Entraînement |
| **TOTAL** | **94%** de couverture |

### Scripts (`scripts/`)

| Script | Usage |
|--------|-------|
| `test_api_prediction.py` | `python scripts/test_api_prediction.py` |
| `promote_model_to_production.py` | `python scripts/promote_model_to_production.py MODEL_NAME` |
| `check_model_features.py` | Vérification compatibilité features |
| `README.md` | Documentation des scripts |

### Configuration

| Fichier | Usage |
|---------|-------|
| `.env` | Variables d'env locales (gitignored) |
| `.env.example` | Template pour devs |
| `.env.docker` | Variables pour Docker Compose |
| `pytest.ini` | Configuration tests |
| `Makefile` | Commandes courantes |

### Docker

| Fichier | Rôle |
|---------|------|
| `Dockerfile` | Image API FastAPI |
| `docker-compose.yml` | ⭐ Orchestration (MLflow + API) |
| `.dockerignore` | Fichiers à exclure |

---

## 🔄 Flux de données

```
data/
  ├── prédiction_de_la_qualité_de_air.csv  (données brutes)
  │   └── [DVC track]
  │       └── processed_data.csv  (après cleaning)
  │           └── [DVC track]
  │               └── X_train, X_test, y_train, y_test
  │                   └── Modèle entraîné
  │                       └── MLflow Registry
  │                           ├── mlruns/ (artifacts)
  │                           ├── models/ (pkl local)
  │                           └── feature_names.json
  │
  └── → API FastAPI
      ├── Charge depuis MLflow
      ├── Features validation
      ├── Prédiction
      └── Retour JSON
```

---

## 🚀 Déploiement

### Local (développement)
```
src/train_final_model.py
  ↓
models/ + mlflow.db
  ↓
python -m uvicorn src.api:app --reload
  ↓
API running on http://localhost:8000
```

### Docker (production)
```
docker-compose up -d
  ├─ mlflow (port 5000)
  │   └─ mlruns/, models/
  │
  └─ api (port 8000)
      ├─ Charge depuis MLflow
      └─ Prédictions
```

---

## 📊 Arborescence MLflow

```
MLflow Registry
├── Expérience 2: air-quality-no2-prediction
│   ├── Run 1: RF_n100_d None
│   ├── Run 2: RF_n50_d None
│   └── Run 3: RF_n100_d10
│       └── Model Version 1 → Production
│
└── Expérience 3: air-quality-final-model
    └── Run 1: final_production_model
        └── Model Version 2 → Production (après promotion)
```

---

## 🔐 Sécurité

### Fichiers gitignored
```
.env              # Variables d'env locales
mlflow.db         # DB SQLite (données sensibles)
*.pyc, __pycache__
.venv/            # Virtual environment
htmlcov/          # Coverage (optionnel)
.pytest_cache/    # Cache pytest
```

---

## 📈 Métriques du projet

| Métrique | Valeur |
|----------|--------|
| Lignes de code (src) | ~500 |
| Lignes de tests | ~300 |
| Tests | 9 passés |
| Couverture | 94% |
| Endpoints API | 4 |
| Scripts | 3 |
| Documentation | 4 fichiers |

---

## ✅ Checklist de structure

- ✅ `src/` avec code principal et API
- ✅ `tests/` avec couverture 94%
- ✅ `data/` avec DVC tracking
- ✅ `models/` pour artifacts locaux
- ✅ `scripts/` pour utilitaires
- ✅ `docs/` documenté
- ✅ `notebooks/` pour exploration
- ✅ `.github/` avec CI/CD
- ✅ Configuration externalisée
- ✅ Docker pour déploiement

---

## 🔗 Fichiers clés pour démarrer

1. **Entraîner**: `src/train_final_model.py`
2. **Tester**: `scripts/test_api_prediction.py`
3. **Déployer**: `docker-compose.yml`
4. **Documenter**: `docs/api_guide.md`
5. **Automatiser**: `Makefile`

---

**Dernière mise à jour**: Janvier 10, 2026
