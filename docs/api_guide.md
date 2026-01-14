# 📖 Guide d'Utilisation de l'API

## Vue d'ensemble

L'API de prédiction de la qualité de l'air permet de prédire la concentration de dioxyde d'azote (NO2) à partir de données atmosphériques en temps réel.

**Base URL**: `http://localhost:8000`  
**Version**: 1.0.0  
**Documentation interactive**: `http://localhost:8000/docs`

---

## 🚀 Démarrage rapide

### 1. Démarrer l'API

```bash
# Avec Python
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

# Avec Docker
docker-compose up -d
```

### 2. Vérifier la santé

```bash
curl http://localhost:8000/health
```

**Réponse attendue** (200 OK):
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "1",
  "version": "1.0.0"
}
```

---

## 📊 Endpoints

### 1️⃣ `GET /` - Page d'accueil

**Description**: Information générale sur l'API

**Requête**:
```bash
curl http://localhost:8000/
```

**Réponse** (200 OK):
```json
{
  "message": "API de prédiction de la qualité de l'air",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "predict": "/predict",
    "health": "/health",
    "model_info": "/model-info",
    "docs": "/docs"
  }
}
```

---

### 2️⃣ `POST /predict` - Prédire NO2

**Description**: Prédire la concentration de NO2(GT) en µg/m³

**URL**: `http://localhost:8000/predict`

**Méthode**: `POST`

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "CO_GT": 2.6,
  "PT08_S1_CO": 1360.0,
  "NMHC_GT": 150.0,
  "C6H6_GT": 11.9,
  "PT08_S2_NMHC": 1046.0,
  "NOx_GT": 166.0,
  "PT08_S3_NOx": 1056.0,
  "PT08_S4_NO2": 1692.0,
  "PT08_S5_O3": 1268.0,
  "T": 13.6,
  "RH": 48.9,
  "AH": 0.7578
}
```

**Paramètres**:

| Paramètre | Type | Unité | Description |
|-----------|------|-------|-------------|
| `CO_GT` | float | mg/m³ | Concentration de monoxyde de carbone |
| `PT08_S1_CO` | float | - | Capteur PT08.S1(CO) |
| `NMHC_GT` | float | µg/m³ | Hydrocarbures non méthaniques |
| `C6H6_GT` | float | µg/m³ | Benzène |
| `PT08_S2_NMHC` | float | - | Capteur PT08.S2(NMHC) |
| `NOx_GT` | float | ppb | Oxydes d'azote |
| `PT08_S3_NOx` | float | - | Capteur PT08.S3(NOx) |
| `PT08_S4_NO2` | float | - | Capteur PT08.S4(NO2) |
| `PT08_S5_O3` | float | - | Capteur PT08.S5(O3) |
| `T` | float | °C | Température |
| `RH` | float | % | Humidité relative |
| `AH` | float | - | Humidité absolue |

**Réponse** (200 OK):
```json
{
  "prediction": 89.42,
  "model_version": "1",
  "confidence_metrics": {
    "model_loaded": true,
    "model_stage": "Production",
    "mlflow_uri": "sqlite:///mlflow.db"
  }
}
```

**Erreurs**:

| Code | Erreur | Cause |
|------|--------|-------|
| 400 | Bad Request | Paramètres invalides ou manquants |
| 503 | Service Unavailable | Modèle non chargé |

**Exemples cURL**:
```bash
# Prédiction simple
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "CO_GT": 2.6,
    "PT08_S1_CO": 1360.0,
    "NMHC_GT": 150.0,
    "C6H6_GT": 11.9,
    "PT08_S2_NMHC": 1046.0,
    "NOx_GT": 166.0,
    "PT08_S3_NOx": 1056.0,
    "PT08_S4_NO2": 1692.0,
    "PT08_S5_O3": 1268.0,
    "T": 13.6,
    "RH": 48.9,
    "AH": 0.7578
  }'
```

---

### 3️⃣ `GET /health` - Vérifier la santé

**Description**: Vérifier l'état de l'API et du modèle

**URL**: `http://localhost:8000/health`

**Méthode**: `GET`

**Réponse** (200 OK):
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "1",
  "version": "1.0.0"
}
```

**Erreurs**:

| Code | Réponse |
|------|---------|
| 503 | Service indisponible: Modèle non chargé |

**Exemples cURL**:
```bash
curl http://localhost:8000/health
```

---

### 4️⃣ `GET /model-info` - Informations du modèle

**Description**: Récupérer les métadonnées du modèle en production

**URL**: `http://localhost:8000/model-info`

**Méthode**: `GET`

**Réponse** (200 OK):
```json
{
  "model_name": "air-quality-no2-predictor",
  "model_stage": "Production",
  "model_version": "1",
  "n_features": 12,
  "features": [
    "CO(GT)",
    "PT08.S1(CO)",
    "NMHC(GT)",
    "C6H6(GT)",
    "PT08.S2(NMHC)",
    "NOx(GT)",
    "PT08.S3(NOx)",
    "PT08.S4(NO2)",
    "PT08.S5(O3)",
    "T",
    "RH",
    "AH"
  ],
  "metadata": {
    "version": "1",
    "stage": "Production",
    "last_updated": 1704843600000,
    "source": "s3://..."
  }
}
```

**Exemples cURL**:
```bash
curl http://localhost:8000/model-info
```

---

## 🔌 Exemples d'intégration

### Python

```python
import requests

# Configuration
API_URL = "http://localhost:8000/predict"

# Données de prédiction
data = {
    "CO_GT": 2.6,
    "PT08_S1_CO": 1360.0,
    "NMHC_GT": 150.0,
    "C6H6_GT": 11.9,
    "PT08_S2_NMHC": 1046.0,
    "NOx_GT": 166.0,
    "PT08_S3_NOx": 1056.0,
    "PT08_S4_NO2": 1692.0,
    "PT08_S5_O3": 1268.0,
    "T": 13.6,
    "RH": 48.9,
    "AH": 0.7578
}

# Effectuer la prédiction
response = requests.post(API_URL, json=data)

if response.status_code == 200:
    result = response.json()
    print(f"Prédiction NO2: {result['prediction']} µg/m³")
    print(f"Version du modèle: {result['model_version']}")
else:
    print(f"Erreur {response.status_code}: {response.text}")
```

### JavaScript/TypeScript

```typescript
async function predictNO2(input: any) {
  const response = await fetch('http://localhost:8000/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(input)
  });

  if (!response.ok) {
    throw new Error(`Erreur: ${response.statusText}`);
  }

  const result = await response.json();
  console.log(`Prédiction: ${result.prediction} µg/m³`);
  return result;
}

// Utilisation
const input = {
  CO_GT: 2.6,
  PT08_S1_CO: 1360.0,
  NMHC_GT: 150.0,
  C6H6_GT: 11.9,
  PT08_S2_NMHC: 1046.0,
  NOx_GT: 166.0,
  PT08_S3_NOx: 1056.0,
  PT08_S4_NO2: 1692.0,
  PT08_S5_O3: 1268.0,
  T: 13.6,
  RH: 48.9,
  AH: 0.7578
};

predictNO2(input);
```

---

## 🐳 Déploiement Docker

### Avec Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f api

# Arrêter les services
docker-compose down
```

### Variables d'environnement

Créez un fichier `.env` à la racine du projet:

```bash
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
MLFLOW_EXPERIMENT_NAME=air-quality-final-model
API_HOST=0.0.0.0
API_PORT=8000
MODEL_NAME=air-quality-no2-predictor
MODEL_STAGE=Production
LOG_LEVEL=INFO
```

---

## 📈 Cas d'usage

### 1. Monitoring en temps réel

Intégrez l'API dans un système de monitoring pour surveiller les niveaux de NO2:

```python
import schedule
import requests
from datetime import datetime

def monitor_air_quality(data):
    response = requests.post("http://localhost:8000/predict", json=data)
    if response.status_code == 200:
        prediction = response.json()['prediction']
        timestamp = datetime.now().isoformat()
        print(f"{timestamp} - NO2: {prediction} µg/m³")
        
        # Alerter si dépassement de seuil
        if prediction > 100:
            print("⚠️ ALERTE: Dépassement du seuil!")

schedule.every(10).minutes.do(monitor_air_quality, data=sensor_data)
```

### 2. Intégration IoT

```python
# Avec capteurs IoT
from paho.mqtt import client as mqtt_client

def on_message(client, userdata, msg):
    sensor_data = json.loads(msg.payload)
    response = requests.post("http://localhost:8000/predict", json=sensor_data)
    # Traiter la prédiction...
```

---

## ⚠️ Limites et recommandations

1. **Plages de validité**: Les prédictions sont fiables pour les ranges observés en entraînement
2. **Latence**: Environ 10-50ms par requête (dépend du matériel)
3. **Concurrence**: Adaptez le nombre de workers Uvicorn selon vos besoins
4. **Données manquantes**: Tous les paramètres sont obligatoires

---

## 🔐 Sécurité

Pour la production:

```bash
# Activer HTTPS
uvicorn src.api:app --ssl-keyfile=/path/to/key.pem --ssl-certfile=/path/to/cert.pem

# Ajouter authentification (voir FastAPI docs)
# Ajouter rate limiting
# Utiliser un reverse proxy (Nginx, etc.)
```

---

## 📞 Support et troubleshooting

### L'API ne démarre pas

```bash
# Vérifier que MLflow est accessible
curl http://localhost:5000/

# Vérifier les logs
docker-compose logs api
```

### Le modèle n'est pas chargé

```bash
# Vérifier que le modèle existe dans MLflow
mlflow ui

# Entraîner et déployer un nouveau modèle
python src/train_final_model.py
```

### Erreur 503 Service Unavailable

Le modèle n'est pas chargé. Vérifiez:
1. Le service MLflow est en cours d'exécution
2. Les variables `MODEL_NAME` et `MODEL_STAGE` sont correctes
3. Le modèle existe en stage Production dans MLflow

---

## 📚 Ressources supplémentaires

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MLflow Documentation](https://www.mlflow.org/)
- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)

---

**Dernière mise à jour**: Janvier 2026
