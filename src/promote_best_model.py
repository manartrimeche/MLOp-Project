import mlflow
from mlflow.tracking import MlflowClient

# Configuration
mlflow.set_tracking_uri("sqlite:///mlflow.db")
client = MlflowClient()

# Chercher le MEILLEUR run (MAE le plus bas)
experiment = client.get_experiment_by_name("air-quality-no2-prediction")
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.mae ASC"],  # Trier par MAE croissant
    max_results=1
)

best_run = runs[0]
best_run_id = best_run.info.run_id
mae = best_run.data.metrics.get("mae")
rmse = best_run.data.metrics.get("rmse")
r2 = best_run.data.metrics.get("r2")

print(f"📊 Meilleur modèle trouvé automatiquement")
print(f"   Run ID: {best_run_id}")
print(f"   MAE : {mae:.2f}")
print(f"   RMSE: {rmse:.2f}")
print(f"   R²  : {r2:.4f}")

# Trouver la version du modèle dans le Registry
model_name = "air-quality-no2-predictor"
versions = client.search_model_versions(f"run_id='{best_run_id}'")

if versions:
    version = versions[0].version
    print(f"\n🔍 Version trouvée: {version}")
    
    # Utiliser les ALIASES (méthode moderne MLflow 2.9+)
    client.set_registered_model_alias(
        name=model_name,
        alias="champion",  # Alias pour le meilleur modèle
        version=version
    )
    
    print(f"✅ Alias 'champion' assigné à la version {version}")
    
    # Ajouter une description
    client.update_model_version(
        name=model_name,
        version=version,
        description=f"Champion model - MAE: {mae:.2f}, RMSE: {rmse:.2f}, R²: {r2:.4f}"
    )
    print(f"📝 Description ajoutée")
else:
    print("❌ Aucune version trouvée pour ce Run ID")
