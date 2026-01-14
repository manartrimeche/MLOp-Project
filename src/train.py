# src/train.py
import os
import pathlib
import joblib
import json
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from data_prep import load_regression_data

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "random_forest_no2_model.pkl"
FEATURES_PATH = MODELS_DIR / "feature_names.json"

# Configuration MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "air-quality-no2-prediction")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)


def train_random_forest(n_estimators=100, max_depth=None, min_samples_split=2, random_state=42):
    """
    Entraîne un RandomForest et log tout dans MLflow
    """
    print(">>> Début de l'entraînement RandomForest")
    
    # Charger les données
    X_train, X_test, y_train, y_test = load_regression_data()
    print(">>> Données chargées :", X_train.shape, X_test.shape)

    # Sauvegarder les noms des features
    feature_names = X_train.columns.tolist()
    
    # Démarrer un run MLflow
    with mlflow.start_run(run_name=f"RF_n{n_estimators}_d{max_depth}"):
        
        # Logger les paramètres
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("min_samples_split", min_samples_split)
        mlflow.log_param("random_state", random_state)
        mlflow.log_param("n_features", X_train.shape[1])
        
        # Entraîner le modèle
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=random_state,
            n_jobs=-1
        )
        model.fit(X_train, y_train)

        # Prédictions et métriques
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = mean_squared_error(y_test, y_pred) ** 0.5
        r2 = r2_score(y_test, y_pred)

        # Logger les métriques
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

        print("RandomForest - NO2(GT)")
        print("MAE :", mae)
        print("RMSE:", rmse)
        print("R²  :", r2)

        # Sauvegarder le modèle localement
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        
        # Sauvegarder les noms des features
        with open(FEATURES_PATH, 'w') as f:
            json.dump(feature_names, f, indent=2)
        
        # Logger le modèle dans MLflow
        mlflow.sklearn.log_model(model, name="model",
registered_model_name="air-quality-no2-predictor"  # Nom dans le Registry
)


        
        # Logger les fichiers
        mlflow.log_artifact(str(FEATURES_PATH))
        
        print(f"✅ Modèle sauvegardé dans {MODEL_PATH}")
        print(f"✅ Run MLflow terminé")


if __name__ == "__main__":
    try:
        # Baseline
        train_random_forest(n_estimators=100, max_depth=None, min_samples_split=2)
        
        # Variation 1 : moins d'arbres
        train_random_forest(n_estimators=50, max_depth=None, min_samples_split=2)
        
        # Variation 2 : profondeur limitée
        train_random_forest(n_estimators=100, max_depth=10, min_samples_split=2)
        
    except Exception as e:
        print("❌ ERREUR pendant l'entraînement :", e)
