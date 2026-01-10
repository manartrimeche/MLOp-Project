import mlflow.pyfunc
import pandas as pd

mlflow.set_tracking_uri("sqlite:///mlflow.db")

# Charger le modèle champion
model = mlflow.pyfunc.load_model("models:/air-quality-no2-predictor@champion")

# Essayer de récupérer les noms de features
try:
    # Pour sklearn, on peut accéder au modèle sous-jacent
    sklearn_model = model._model_impl.sklearn_model
    if hasattr(sklearn_model, 'feature_names_in_'):
        print("Features attendues par le modèle:")
        print(sklearn_model.feature_names_in_)
    else:
        print("Impossible de récupérer les noms de features")
except Exception as e:
    print(f"Erreur: {e}")
    
# Charger le dataset pour voir l'ordre des colonnes
print("\nColonnes du dataset d'origine:")
df = pd.read_csv("data/prediction_de_la_qualite_de_air.csv", sep=";", decimal=",")
# Exclure NO2(GT) qui est la target
features = [col for col in df.columns if col not in ['NO2(GT)', 'Date', 'Time']]
print(features)
