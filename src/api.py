from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import mlflow.pyfunc
import pandas as pd
import numpy as np
from typing import List
from pydantic import BaseModel, Field

# Configuration
mlflow.set_tracking_uri("sqlite:///mlflow.db")

# Charger le modèle champion
try:
    model = mlflow.pyfunc.load_model("models:/air-quality-no2-predictor@champion")
    print("✅ Modèle 'champion' chargé avec succès")
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle: {e}")
    model = None

# Initialiser FastAPI
app = FastAPI(
    title="Air Quality NO2 Prediction API",
    description="API de prédiction de la qualité de l'air (NO2) utilisant MLflow",
    version="1.0.0"
)

# Schéma des données d'entrée
class AirQualityInput(BaseModel):
    CO_GT: float = Field(..., alias="CO(GT)", description="CO ground truth")
    PT08_S1_CO: float = Field(..., alias="PT08.S1(CO)", description="Sensor 1 (CO)")
    NMHC_GT: float = Field(..., alias="NMHC(GT)", description="NMHC ground truth")
    C6H6_GT: float = Field(..., alias="C6H6(GT)", description="Benzene ground truth")
    PT08_S2_NMHC: float = Field(..., alias="PT08.S2(NMHC)", description="Sensor 2 (NMHC)")
    NOx_GT: float = Field(..., alias="NOx(GT)", description="NOx ground truth")
    PT08_S3_NOx: float = Field(..., alias="PT08.S3(NOx)", description="Sensor 3 (NOx)")
    PT08_S4_NO2: float = Field(..., alias="PT08.S4(NO2)", description="Sensor 4 (NO2)")
    PT08_S5_O3: float = Field(..., alias="PT08.S5(O3)", description="Sensor 5 (O3)")
    T: float = Field(..., description="Temperature")
    RH: float = Field(..., description="Relative Humidity")
    AH: float = Field(..., description="Absolute Humidity")
    
    class Config:
        populate_by_name = True  # Permet d'utiliser alias ou nom de champ
        schema_schema_extra = {
            "example": {
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
        }

class PredictionOutput(BaseModel):
    prediction: float = Field(..., description="Valeur prédite de NO2(GT)")
    model_version: str = Field(..., description="Version du modèle utilisé")

# Routes API
@app.get("/")
def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Air Quality NO2 Prediction API",
        "status": "running",
        "model_loaded": model is not None,
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Vérification de l'état de l'API"""
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    return {"status": "healthy", "model": "loaded"}

@app.post("/predict", response_model=PredictionOutput)
def predict(input_data: AirQualityInput):
    """
    Prédiction de la concentration de NO2
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    
    try:
        # Convertir en DataFrame avec les VRAIS noms de colonnes attendus par le modèle
        data_dict = {
            "CO(GT)": input_data.CO_GT,
            "PT08.S1(CO)": input_data.PT08_S1_CO,
            "NMHC(GT)": input_data.NMHC_GT,
            "C6H6(GT)": input_data.C6H6_GT,
            "PT08.S2(NMHC)": input_data.PT08_S2_NMHC,
            "NOx(GT)": input_data.NOx_GT,
            "PT08.S3(NOx)": input_data.PT08_S3_NOx,
            "PT08.S4(NO2)": input_data.PT08_S4_NO2,
            "PT08.S5(O3)": input_data.PT08_S5_O3,
            "T": input_data.T,
            "RH": input_data.RH,
            "AH": input_data.AH
        }
        
        input_df = pd.DataFrame([data_dict])
        
        # Faire la prédiction
        prediction = model.predict(input_df)[0]
        
        return {
            "prediction": float(prediction),
            "model_version": "champion (v1)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

@app.post("/predict/batch")
def predict_batch(input_data: List[AirQualityInput]):
    """
    Prédictions multiples en batch
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    
    try:
        # Convertir chaque élément avec les bons noms de colonnes
        data_list = []
        for item in input_data:
            data_dict = {
                "CO(GT)": item.CO_GT,
                "PT08.S1(CO)": item.PT08_S1_CO,
                "NMHC(GT)": item.NMHC_GT,
                "C6H6(GT)": item.C6H6_GT,
                "PT08.S2(NMHC)": item.PT08_S2_NMHC,
                "NOx(GT)": item.NOx_GT,
                "PT08.S3(NOx)": item.PT08_S3_NOx,
                "PT08.S4(NO2)": item.PT08_S4_NO2,
                "PT08.S5(O3)": item.PT08_S5_O3,
                "T": item.T,
                "RH": item.RH,
                "AH": item.AH
            }
            data_list.append(data_dict)
        
        input_df = pd.DataFrame(data_list)
        
        # Faire les prédictions
        predictions = model.predict(input_df)
        
        return {
            "predictions": predictions.tolist(),
            "count": len(predictions),
            "model_version": "champion (v1)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")
