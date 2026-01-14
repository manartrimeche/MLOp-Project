# 🔧 Scripts d'Utilitaire

Ce dossier contient les scripts d'utilitaire pour gérer le projet MLOps.

## 📋 Scripts disponibles

### 1. `test_api_prediction.py`

**Objectif**: Tester les endpoints de l'API

**Usage**:
```bash
python scripts/test_api_prediction.py
# ou avec une URL personnalisée
python scripts/test_api_prediction.py --url http://localhost:8000
```

**Tests effectués**:
- ✅ Endpoint racine (`GET /`)
- ✅ Health check (`GET /health`)
- ✅ Informations du modèle (`GET /model-info`)
- ✅ Prédiction valide (`POST /predict`)
- ✅ Validation des données (`POST /predict` avec données invalides)

**Exemple de sortie**:
```
==============================================================================
🧪 TEST DE L'API AIR QUALITY PREDICTION
==============================================================================

[1/5] Test GET /
  ✅ PASS

[2/5] Test GET /health
  ✅ PASS: API et modèle sain

[3/5] Test GET /model-info
  ✅ PASS
     - Modèle: air-quality-no2-predictor
     - Version: 1
     - Features: 12

[4/5] Test POST /predict (données valides)
  ✅ PASS
     - Prédiction: 89.42 µg/m³
     - Modèle version: 1

[5/5] Test POST /predict (données invalides)
  ✅ PASS: Validation correcte (422)

==============================================================================
✅ TOUS LES TESTS SONT PASSÉS!
==============================================================================
```

---

### 2. `promote_model_to_production.py`

**Objectif**: Promouvoir un modèle du stage Staging à Production dans MLflow Registry

**Usage**:
```bash
python scripts/promote_model_to_production.py air-quality-no2-predictor
# ou pour une version spécifique
python scripts/promote_model_to_production.py air-quality-no2-predictor 1
```

**Actions effectuées**:
1. Récupère la dernière version en Staging
2. Archive la version Production existante
3. Promeut la nouvelle version en Production

**Exemple de sortie**:
```
🔄 Promotion du modèle 'air-quality-no2-predictor' en Production...
   Tracking URI: sqlite:///mlflow.db

✅ Modèle trouvé:
   - Version: 2
   - Stage actuel: Staging
   - Source: mlruns/3/...

📦 Ancienne version 1 archivée

✅ SUCCESS: Modèle v2 promu en Production!
```

---

### 3. `check_model_features.py`

**Objectif**: Vérifier la compatibilité des features entre le modèle et les données

**Usage**:
```bash
python scripts/check_model_features.py
```

---

## 🔄 Workflow type

### 1. Entraînement et test local

```bash
# Entraîner le modèle
python src/train_final_model.py

# Démarrer l'API
python -m uvicorn src.api:app --reload

# Tester dans un autre terminal
python scripts/test_api_prediction.py
```

### 2. Déploiement Docker

```bash
# Démarrer tous les services
docker-compose up -d

# Attendre que MLflow soit prêt (30-40s)
sleep 40

# Tester l'API
python scripts/test_api_prediction.py

# Vérifier les logs
docker-compose logs -f api
```

### 3. Promotion en Production

```bash
# Si le modèle n'est pas déjà en Production
python scripts/promote_model_to_production.py air-quality-no2-predictor

# Redémarrer l'API pour charger la nouvelle version
docker-compose restart api

# Tester à nouveau
python scripts/test_api_prediction.py
```

---

## 📊 Variables d'environnement

Les scripts utilisent ces variables d'environnement (optionnelles):

```bash
# MLflow
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
MLFLOW_EXPERIMENT_NAME=air-quality-final-model

# API
API_HOST=0.0.0.0
API_PORT=8000
MODEL_NAME=air-quality-no2-predictor
MODEL_STAGE=Production
```

---

## ⚠️ Troubleshooting

### "Connection refused" lors du test d'API

```bash
# Vérifier que l'API est running
curl http://localhost:8000/health

# Si ne répond pas, démarrer l'API
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### Modèle non trouvé dans MLflow

```bash
# Vérifier les modèles disponibles
mlflow ui  # Ouvrir http://localhost:5000

# Entraîner un nouveau modèle
python src/train_final_model.py

# Promouvoir le modèle
python scripts/promote_model_to_production.py air-quality-no2-predictor
```

### MLflow inaccessible en Docker

```bash
# Vérifier que le service MLflow est running
docker-compose ps

# Vérifier les logs
docker-compose logs mlflow

# Redémarrer le service
docker-compose restart mlflow
```

---

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MLflow Documentation](https://www.mlflow.org/docs/latest/index.html)
- [Guide complet de l'API](../docs/api_guide.md)

---

**Dernière mise à jour**: Janvier 2026
