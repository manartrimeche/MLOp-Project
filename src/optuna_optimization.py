import optuna
import mlflow
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
import joblib
warnings.filterwarnings('ignore')

# Configuration MLflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("air-quality-optuna-optimization")

# Charger les données
print("📊 Chargement des données...")
df = pd.read_csv("data/processed_data.csv")

# Séparer features et target
X = df.drop(['NO2(GT)', 'Date', 'Time'], axis=1, errors='ignore')
y = df['NO2(GT)']

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Dataset: {len(X)} échantillons, {X.shape[1]} features")
print(f"Train: {len(X_train)}, Test: {len(X_test)}")
print("-" * 60)

def objective(trial):
    """Fonction objective pour Optuna"""
    
    # Suggérer des hyperparamètres
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 200, step=10),
        'max_depth': trial.suggest_int('max_depth', 5, 20),
        'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 4),
        'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2']),
        'random_state': 42
    }
    
    # Entraîner le modèle
    model = RandomForestRegressor(**params, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Prédictions
    y_pred = model.predict(X_test)
    
    # Calculer les métriques
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # Logger dans MLflow
    with mlflow.start_run(run_name=f"optuna_trial_{trial.number}"):
        mlflow.log_params(params)
        mlflow.log_metrics({
            "mae": mae,
            "rmse": rmse,
            "r2": r2
        })
        mlflow.log_param("trial_number", trial.number)
        mlflow.log_param("optimizer", "optuna")
        
        # Logger le modèle
        mlflow.sklearn.log_model(model, "model")
    
    print(f"Trial {trial.number:2d}: MAE = {mae:6.3f}, RMSE = {rmse:6.3f}, R² = {r2:.4f}")
    
    # Retourner la métrique à minimiser
    return mae

if __name__ == "__main__":
    print("\n🔬 DÉMARRAGE DE L'OPTIMISATION OPTUNA")
    print("=" * 60)
    
    # Créer une étude Optuna
    study = optuna.create_study(
        direction='minimize',
        study_name='air-quality-rf-optimization',
        sampler=optuna.samplers.TPESampler(seed=42)
    )
    
    # Optimiser (10 trials comme demandé dans le cahier des charges)
    study.optimize(objective, n_trials=10, show_progress_bar=True)
    
    print("\n" + "=" * 60)
    print("🏆 RÉSULTATS DE L'OPTIMISATION")
    print("=" * 60)
    print(f"\n✅ Meilleur MAE: {study.best_value:.4f}")
    print(f"\n🎯 Meilleurs hyperparamètres:")
    for param, value in study.best_params.items():
        print(f"  - {param:20s}: {value}")
    
    # Sauvegarder l'étude
    joblib.dump(study, 'models/optuna_study.pkl')
    print(f"\n💾 Étude sauvegardée: models/optuna_study.pkl")
    
    # Afficher l'importance des paramètres
    print("\n📊 Importance des hyperparamètres:")
    try:
        importance = optuna.importance.get_param_importances(study)
        for param, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {param:20s}: {imp:.4f}")
    except:
        print("  (Pas assez de trials pour calculer l'importance)")
    
    print("\n" + "=" * 60)
    print("✅ Optimisation terminée avec succès!")
    print("=" * 60)
