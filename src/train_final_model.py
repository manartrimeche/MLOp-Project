# src/train_final_model.py
import pandas as pd
import pickle
import pathlib
import numpy as np  # ← AJOUTER CETTE LIGNE
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import mlflow
import mlflow.sklearn

print("=" * 60)
print("🚀 ENTRAÎNEMENT DU MODÈLE FINAL")
print("=" * 60)

# Configuration MLflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("air-quality-final-model")

# Charger les données
print("\n📊 Chargement des données...")
df = pd.read_csv("data/processed_data.csv")
X = df.drop(['NO2(GT)', 'Date', 'Time'], axis=1, errors='ignore')
y = df['NO2(GT)']

print(f"   Dataset: {len(df)} échantillons, {X.shape[1]} features")

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"   Train: {len(X_train)}, Test: {len(X_test)}")

# Meilleurs hyperparamètres trouvés par Optuna
best_params = {
    'n_estimators': 140,
    'max_depth': 19,
    'min_samples_split': 2,
    'min_samples_leaf': 1,
    'max_features': 'log2',
    'random_state': 42,
    'n_jobs': -1
}

print("\n🎯 Hyperparamètres optimaux:")
for param, value in best_params.items():
    print(f"   - {param:20s}: {value}")

# Entraîner le modèle final
print("\n⚙️  Entraînement en cours...")
with mlflow.start_run(run_name="final_production_model"):
    model = RandomForestRegressor(**best_params)
    model.fit(X_train, y_train)
    
    # Prédictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Métriques sur train
    mae_train = mean_absolute_error(y_train, y_pred_train)
    rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))  # ← CORRIGÉ
    r2_train = r2_score(y_train, y_pred_train)
    
    # Métriques sur test
    mae_test = mean_absolute_error(y_test, y_pred_test)
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))  # ← CORRIGÉ
    r2_test = r2_score(y_test, y_pred_test)
    
    print("\n✅ PERFORMANCES DU MODÈLE FINAL")
    print("=" * 60)
    print(f"{'Métrique':<15} {'Train':<15} {'Test':<15}")
    print("-" * 60)
    print(f"{'MAE':<15} {mae_train:<15.4f} {mae_test:<15.4f}")
    print(f"{'RMSE':<15} {rmse_train:<15.4f} {rmse_test:<15.4f}")
    print(f"{'R²':<15} {r2_train:<15.4f} {r2_test:<15.4f}")
    print("=" * 60)
    
    # Log dans MLflow
    mlflow.log_params(best_params)
    mlflow.log_metrics({
        "mae_train": mae_train,
        "rmse_train": rmse_train,
        "r2_train": r2_train,
        "mae_test": mae_test,
        "rmse_test": rmse_test,
        "r2_test": r2_test
    })
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n📊 Importance des features (Top 5):")
    for idx, row in feature_importance.head(5).iterrows():
        print(f"   {row['feature']:20s}: {row['importance']:.4f}")
    
    # Sauvegarder le modèle avec MLflow
    mlflow.sklearn.log_model(
        model, 
        "model",
        registered_model_name="air-quality-model"
    )
    
    # Sauvegarder les feature names
    mlflow.log_dict({"features": list(X.columns)}, "feature_names.json")

# Sauvegarder localement
print("\n💾 Sauvegarde locale du modèle...")
models_dir = pathlib.Path("models")
models_dir.mkdir(exist_ok=True)

model_data = {
    'model': model,
    'feature_names': list(X.columns),
    'best_params': best_params,
    'metrics': {
        'mae_test': mae_test,
        'rmse_test': rmse_test,
        'r2_test': r2_test
    }
}

with open("models/final_model.pkl", "wb") as f:
    pickle.dump(model_data, f)

print(f"   ✓ Modèle sauvegardé: models/final_model.pkl")
print(f"   ✓ Features: {len(X.columns)}")
print("\n" + "=" * 60)
print("✅ MODÈLE FINAL PRÊT POUR LA PRODUCTION")
print("=" * 60)
