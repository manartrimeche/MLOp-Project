# src/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
import os
import pandas as pd
from typing import List
import uvicorn
import mlflow
import mlflow.sklearn
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
MODEL_NAME = os.getenv("MODEL_NAME", "air-quality-no2-predictor")
MODEL_STAGE = os.getenv("MODEL_STAGE", "Production")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Initialiser FastAPI
app = FastAPI(
    title="Air Quality Prediction API",
    description="API pour prédire NO2(GT) à partir des données de qualité de l'air",
    version="1.0.0"
)

# Variables globales pour le modèle
model = None
feature_names = None
model_metadata = None

@app.on_event("startup")
async def load_model():
    """Charger le modèle depuis le fichier local ou MLflow Registry"""
    global model, feature_names, model_metadata
    try:
        logger.info(f"🔄 Chargement du modèle...")
        
        # Essayer d'abord le fichier local
        import pickle
        local_model_path = "models/final_model.pkl"
        if os.path.exists(local_model_path):
            logger.info(f"   Chargement depuis: {local_model_path}")
            with open(local_model_path, "rb") as f:
                loaded_obj = pickle.load(f)
                if isinstance(loaded_obj, dict) and "model" in loaded_obj:
                    logger.info("   Détection d'un paquet modèle dict -> extraction de 'model'")
                    model = loaded_obj["model"]
                    # Utiliser les features locales si disponibles
                    if loaded_obj.get("feature_names"):
                        feature_names = loaded_obj["feature_names"]
                    # Enrichir les métadonnées si disponibles
                    model_metadata = {
                        "source": local_model_path,
                        "version": "local",
                        "stage": "local",
                        "metrics": loaded_obj.get("metrics", {})
                    }
                else:
                    model = loaded_obj
        else:
            # Fallback sur MLflow Registry
            logger.info(f"🔄 Chargement du modèle depuis MLflow...")
            logger.info(f"   URI: {MLFLOW_TRACKING_URI}")
            logger.info(f"   Modèle: {MODEL_NAME}")
            logger.info(f"   Stage: {MODEL_STAGE}")
            
            model = mlflow.sklearn.load_model(
                f"models:/{MODEL_NAME}/{MODEL_STAGE}"
            )
        
        # Charger les feature names
        try:
            if not feature_names:
                with open("models/feature_names.json", "r") as f:
                    import json
                    feature_names = json.load(f)
        except FileNotFoundError:
            logger.warning("⚠️  Feature names non trouvés, en inférant depuis le modèle")
            feature_names = None
        
        # Récupérer les métadonnées
        client = mlflow.tracking.MlflowClient()
        try:
            model_version = client.get_latest_versions(MODEL_NAME, stages=[MODEL_STAGE])[0]
            model_metadata = {
                "version": model_version.version,
                "stage": model_version.current_stage,
                "last_updated": model_version.last_updated_timestamp,
                "source": model_version.source
            }
        except Exception as e:
            logger.warning(f"⚠️  Impossible de récupérer les métadonnées: {e}")
            model_metadata = {}
        
        logger.info("✅ Modèle chargé avec succès")
        if feature_names:
            logger.info(f"   Features: {len(feature_names)}")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement du modèle: {e}")
        logger.error("   Assurez-vous que:")
        logger.error(f"   1. MLflow est configuré (MLFLOW_TRACKING_URI={MLFLOW_TRACKING_URI})")
        logger.error(f"   2. Le modèle '{MODEL_NAME}' existe en stage '{MODEL_STAGE}'")
        logger.error("   3. Vous avez exécuté: python src/train_final_model.py")
        # Ne pas lever d'exception pour permettre au serveur de démarrer
        # mais les requêtes de prédiction échoueront

# Définir le schéma d'entrée
class AirQualityInput(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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
        }
    )
    
    CO_GT: float = Field(..., description="CO en mg/m^3")
    PT08_S1_CO: float = Field(..., description="Capteur PT08.S1(CO)")
    NMHC_GT: float = Field(..., description="NMHC en µg/m^3")
    C6H6_GT: float = Field(..., description="Benzène en µg/m^3")
    PT08_S2_NMHC: float = Field(..., description="Capteur PT08.S2(NMHC)")
    NOx_GT: float = Field(..., description="NOx en ppb")
    PT08_S3_NOx: float = Field(..., description="Capteur PT08.S3(NOx)")
    PT08_S4_NO2: float = Field(..., description="Capteur PT08.S4(NO2)")
    PT08_S5_O3: float = Field(..., description="Capteur PT08.S5(O3)")
    T: float = Field(..., description="Température en °C")
    RH: float = Field(..., description="Humidité relative en %")
    AH: float = Field(..., description="Humidité absolue")

class PredictionOutput(BaseModel):
    prediction: float = Field(..., description="Prédiction NO2(GT) en µg/m^3")
    model_version: str = Field(..., description="Version du modèle")
    confidence_metrics: dict = Field(..., description="Métriques de confiance")

# Route principale
@app.get("/")
def root():
    """Page d'accueil de l'API"""
    return {
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

# Route de prédiction
@app.post("/predict", response_model=PredictionOutput)
def predict(input_data: AirQualityInput):
    """
    Prédire la concentration de NO2(GT)
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé. Veuillez réessayer.")
    
    try:
        # Convertir en DataFrame avec les bons noms de colonnes
        input_dict = {
            'CO(GT)': input_data.CO_GT,
            'PT08.S1(CO)': input_data.PT08_S1_CO,
            'NMHC(GT)': input_data.NMHC_GT,
            'C6H6(GT)': input_data.C6H6_GT,
            'PT08.S2(NMHC)': input_data.PT08_S2_NMHC,
            'NOx(GT)': input_data.NOx_GT,
            'PT08.S3(NOx)': input_data.PT08_S3_NOx,
            'PT08.S4(NO2)': input_data.PT08_S4_NO2,
            'PT08.S5(O3)': input_data.PT08_S5_O3,
            'T': input_data.T,
            'RH': input_data.RH,
            'AH': input_data.AH
        }
        
        df = pd.DataFrame([input_dict])
        
        # Prédiction
        prediction = model.predict(df)[0]
        
        return PredictionOutput(
            prediction=round(float(prediction), 2),
            model_version=str(model_metadata.get("version", "unknown")) if model_metadata else "unknown",
            confidence_metrics={
                "model_loaded": True,
                "model_stage": MODEL_STAGE,
                "mlflow_uri": MLFLOW_TRACKING_URI
            }
        )
    
    except Exception as e:
        logger.error(f"Erreur de prédiction: {e}")
        raise HTTPException(status_code=400, detail=f"Erreur de prédiction: {str(e)}")

# Route de santé
@app.get("/health")
def health_check():
    """Vérifier l'état de l'API"""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Service indisponible: Modèle non chargé"
        )
    
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_version": str(model_metadata.get("version", "unknown")) if model_metadata else "unknown",
        "version": "1.0.0"
    }

# Route d'informations sur le modèle
@app.get("/model-info")
def model_info():
    """Obtenir les informations du modèle"""
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    return {
        "model_name": MODEL_NAME,
        "model_stage": MODEL_STAGE,
        "model_version": str(model_metadata.get("version", "unknown")) if model_metadata else "unknown",
        "n_features": len(feature_names) if feature_names else "unknown",
        "features": feature_names if feature_names else "unknown",
        "metadata": model_metadata or {}
    }

if __name__ == "__main__":
    print("🚀 Démarrage de l'API Air Quality Prediction...")
    print("📖 Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
