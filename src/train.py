# src/train.py
import os
import pathlib
import joblib
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from data_prep import load_regression_data

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "random_forest_no2_model.pkl"
FEATURES_PATH = MODELS_DIR / "feature_names.json"


def train_random_forest():
    print(">>> Script train.py lancé")
    print(">>> Début de l'entraînement RandomForest")
    
    X_train, X_test, y_train, y_test = load_regression_data()
    print(">>> Données chargées :", X_train.shape, X_test.shape)

    # Sauvegarder les noms de colonnes
    feature_names = X_train.columns.tolist()
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=None,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2 = r2_score(y_test, y_pred)

    print("RandomForest - NO2(GT)")
    print("MAE :", mae)
    print("RMSE:", rmse)
    print("R²  :", r2)

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    
    # Sauvegarder les noms des features
    with open(FEATURES_PATH, 'w') as f:
        json.dump(feature_names, f, indent=2)
    
    print(f"✅ Modèle sauvegardé dans {MODEL_PATH}")
    print(f"✅ Features sauvegardées dans {FEATURES_PATH}")


if __name__ == "__main__":
    try:
        train_random_forest()
    except Exception as e:
        print("❌ ERREUR pendant l'entraînement :", e)
