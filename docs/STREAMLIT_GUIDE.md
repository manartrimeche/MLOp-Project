# 🎨 Streamlit App - Guide d'utilisation

Application Streamlit simple pour prédire la concentration de NO₂ basée sur les données de capteurs de qualité de l'air.

## 📋 Prérequis

1. **API FastAPI lancée** sur `http://localhost:8000`
2. **Modèle entraîné** et promu en stage `Production`
3. **Streamlit et Plotly installés**

## 🚀 Lancement

### Option 1: Via le terminal PowerShell

```powershell
# Depuis le répertoire du projet
cd C:\Users\RSCH\MLOp-Project

# Activer l'environnement virtuel
.\.venv\Scripts\Activate.ps1

# Lancer Streamlit
streamlit run app.py
```

L'application s'ouvrira automatiquement sur `http://localhost:8501`

### Option 2: Depuis le Makefile (Linux/Mac)

```bash
make streamlit
```

## 📱 Fonctionnalités

### 1️⃣ **Prédiction** 
- Formulaire interactif pour entrer les paramètres des capteurs
- Prédiction instantanée de NO₂
- Affichage de la confiance du modèle

### 2️⃣ **Données de test**
Trois cas prédéfinis:
- **Cas Normal**: Pollution standard
- **Pollution élevée**: Concentrations élevées
- **Pollution faible**: Concentrations basses

### 3️⃣ **Infos Modèle**
- Version et stage du modèle
- Métriques de performance (MAE, RMSE, R²)
- Importance des features (top 10)

### 4️⃣ **Historique**
- Historique des prédictions effectuées
- Graphiques de l'évolution NO₂
- Statistiques (moyenne, max, min)

## 🔧 Architecture

```
┌─────────────────────┐
│   Streamlit App     │
│   (Frontend)        │ :8501
│  ├─ Prédiction      │
│  ├─ Données test    │
│  ├─ Infos modèle    │
│  └─ Historique      │
└──────────┬──────────┘
           │ requests
           ▼
┌──────────────────────┐
│  FastAPI Server      │
│  (src/api.py)        │ :8000
│  ├─ POST /predict    │
│  ├─ GET /health      │
│  └─ GET /model-info  │
└──────────┬───────────┘
           │ mlflow.sklearn.load_model()
           ▼
┌──────────────────────┐
│   MLflow Registry    │
│   (models/)          │
│   └─ air-quality-    │
│      no2-predictor   │
└──────────────────────┘
```

## 📊 Paramètres d'entrée

| Paramètre | Unité | Exemple | Description |
|-----------|-------|---------|-------------|
| CO_GT | mg/m³ | 2.6 | Monoxyde de carbone |
| PT08_S1_CO | - | 1360.0 | Capteur PT08.S1(CO) |
| NMHC_GT | µg/m³ | 150.0 | Composés organiques non méthaniques |
| C6H6_GT | µg/m³ | 11.9 | Benzène |
| PT08_S2_NMHC | - | 1046.0 | Capteur PT08.S2(NMHC) |
| NOx_GT | ppb | 166.0 | Oxydes d'azote |
| PT08_S3_NOx | - | 1056.0 | Capteur PT08.S3(NOx) |
| PT08_S4_NO2 | - | 1692.0 | Capteur PT08.S4(NO2) |
| PT08_S5_O3 | - | 1268.0 | Capteur PT08.S5(Ozone) |
| T | °C | 13.6 | Température |
| RH | % | 48.9 | Humidité relative |
| AH | - | 0.7578 | Humidité absolue |

## 🧪 Exemple d'utilisation

1. **Lancer l'API** (terminal 1):
```powershell
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

2. **Lancer Streamlit** (terminal 2):
```powershell
streamlit run app.py
```

3. **Naviguer dans l'app**:
   - Aller sur `http://localhost:8501`
   - Sélectionner "Prédiction" dans la sidebar
   - Modifier les paramètres ou utiliser les données de test
   - Cliquer sur "🚀 Prédire NO₂"

## 🐛 Dépannage

### ❌ "Impossible de se connecter à l'API"
→ Assurez-vous que l'API est lancée sur le port 8000

### ❌ "Modèle non chargé"
→ Le modèle n'est pas en stage `Production`. Lancez:
```powershell
python scripts/promote_model_to_production.py air-quality-no2-predictor 3
```

### ❌ "Erreur lors du chargement de Streamlit"
→ Installez les dépendances:
```powershell
pip install streamlit plotly
```

## 📈 Performances attendues

Pour l'ensemble de test:
- **MAE**: ~10.2 µg/m³
- **RMSE**: ~15.1 µg/m³
- **R²**: 0.9849 (98.49% de variance expliquée)

## 🎯 Prochaines améliorations

- [ ] Export des prédictions en CSV
- [ ] Graphiques de corrélation
- [ ] Alertes de pollution
- [ ] Comparaison multi-modèles
- [ ] Intégration avec données météo en temps réel

---

**Note**: L'application utilise des données locales. Pour la production, modifier `API_URL` pour pointer vers votre serveur.
