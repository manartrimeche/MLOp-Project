# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pathlib
import pandas as pd
import traceback
import json

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "random_forest_no2_model.pkl"
FEATURES_PATH = PROJECT_ROOT / "models" / "feature_names.json"

model = joblib.load(MODEL_PATH)

# Charger les noms de features attendues
with open(FEATURES_PATH, 'r') as f:
    feature_names = json.load(f)

app = FastAPI(title="API Prédiction NO2", version="1.0.0")


class AirQualityInput(BaseModel):
    CO_GT: float
    NMHC_GT: float
    C6H6_GT: float
    NOx_GT: float
    PT08_S1_CO: float
    PT08_S2_NMHC: float
    PT08_S3_NOx: float
    PT08_S4_NO2: float
    PT08_S5_O3: float
    T: float
    RH: float
    AH: float


@app.get("/")
def read_root():
    return {"message": "API de prédiction de NO2(GT) - qualité de l'air"}


@app.post("/predict")
def predict_no2(data: AirQualityInput):
    try:
        # Créer le dictionnaire avec TOUS les champs attendus
        input_dict = {
            "CO(GT)": data.CO_GT,
            "NMHC(GT)": data.NMHC_GT,
            "C6H6(GT)": data.C6H6_GT,
            "NOx(GT)": data.NOx_GT,
            "PT08.S1(CO)": data.PT08_S1_CO,
            "PT08.S2(NMHC)": data.PT08_S2_NMHC,
            "PT08.S3(NOx)": data.PT08_S3_NOx,
            "PT08.S4(NO2)": data.PT08_S4_NO2,
            "PT08.S5(O3)": data.PT08_S5_O3,
            "T": data.T,
            "RH": data.RH,
            "AH": data.AH
        }

        # Créer le DataFrame avec les colonnes dans le bon ordre
        df = pd.DataFrame([input_dict])
        df = df[feature_names]  # Réordonner selon l'ordre d'entraînement

        prediction = model.predict(df)[0]

        return {"prediction_NO2_GT": float(prediction)}
        
    except Exception as e:
        error_detail = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction: {str(e)}\n\nTraceback:\n{error_detail}"
        )
