import pandas as pd
import numpy as np
import pathlib
from zenml import step, pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import mlflow
import joblib
import json

@step
def data_loader() -> pd.DataFrame:
    """Loads raw data from csv."""
    project_root = pathlib.Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "prédiction_de_la_qualité_de_air.csv"
    df = pd.read_csv(data_path, sep=';')
    df = df.dropna(axis=1, how='all')
    df.columns = df.columns.str.strip()
    return df

@step
def data_cleaner(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and prepares data."""
    colonnes_numeriques = [col for col in df.columns if col not in ['Date', 'Time']]
    for col in colonnes_numeriques:
        df[col] = df[col].astype(str).str.replace(',', '.')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in df.select_dtypes(include='number').columns:
        df[col] = df[col].fillna(df[col].mean())
    return df

@step
def model_trainer(df: pd.DataFrame) -> RandomForestRegressor:
    """Trains a Random Forest model."""
    X = df.drop(columns=['NO2(GT)', 'Date', 'Time'], errors='ignore')
    y = df['NO2(GT)']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

@step
def model_evaluator(model: RandomForestRegressor, df: pd.DataFrame) -> dict:
    """Evaluates the model and logs to MLflow."""
    X = df.drop(columns=['NO2(GT)', 'Date', 'Time'], errors='ignore')
    y = df['NO2(GT)']
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    metrics = {"mae": mae, "rmse": rmse, "r2": r2}
    print(f"Model Evaluation: {metrics}")
    return metrics

@step
def model_exporter(model: RandomForestRegressor, df: pd.DataFrame, metrics: dict):
    """Exports the model and features list in the production format."""
    import pickle
    project_root = pathlib.Path(__file__).resolve().parents[1]
    models_dir = project_root / "models"
    models_dir.mkdir(exist_ok=True)
    
    X = df.drop(columns=['NO2(GT)', 'Date', 'Time'], errors='ignore')
    
    model_data = {
        'model': model,
        'feature_names': X.columns.tolist(),
        'best_params': model.get_params(),
        'metrics': {
            'mae_test': metrics['mae'],
            'rmse_test': metrics['rmse'],
            'r2_test': metrics['r2']
        }
    }
    
    # Save model data
    with open(models_dir / "final_model.pkl", "wb") as f:
        pickle.dump(model_data, f)
    
    # Also save the old format for backward compatibility if needed
    joblib.dump(model, models_dir / "random_forest_no2_model.pkl")
    with open(models_dir / "feature_names.json", "w") as f:
        json.dump(X.columns.tolist(), f)
    
    print("✅ Model and metadata exported to models/final_model.pkl")

@pipeline
def air_quality_pipeline():
    """End-to-end training pipeline."""
    raw_data = data_loader()
    cleaned_data = data_cleaner(raw_data)
    model = model_trainer(cleaned_data)
    metrics = model_evaluator(model, cleaned_data)
    model_exporter(model, cleaned_data, metrics)

if __name__ == "__main__":
    air_quality_pipeline()
