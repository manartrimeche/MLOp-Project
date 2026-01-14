#!/usr/bin/env python
# scripts/promote_model_to_production.py
"""
Script pour promouvoir un modèle de Staging à Production dans MLflow Registry.
Utilisation: python scripts/promote_model_to_production.py <model_name> <version>
"""

import os
import sys
import mlflow
from mlflow.tracking import MlflowClient

def promote_model(model_name: str, version: str = None):
    """
    Promouvoir un modèle au stage Production
    
    Args:
        model_name: Nom du modèle dans le registry
        version: Version spécifique du modèle (si None, prend la dernière)
    """
    
    # Configuration MLflow
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    mlflow.set_tracking_uri(tracking_uri)
    
    client = MlflowClient()
    
    try:
        print(f"🔄 Promotion du modèle '{model_name}' en Production...")
        print(f"   Tracking URI: {tracking_uri}")
        
        # Récupérer les versions du modèle
        versions = client.get_latest_versions(model_name, stages=["Staging"])
        
        if not versions:
            print(f"❌ Aucune version en Staging trouvée pour '{model_name}'")
            return False
        
        # Prendre la dernière version Staging
        model_version = versions[0]
        version_num = model_version.version
        
        print(f"\n✅ Modèle trouvé:")
        print(f"   - Version: {version_num}")
        print(f"   - Stage actuel: {model_version.current_stage}")
        print(f"   - Source: {model_version.source}")
        
        # Archiver la version Production existante
        try:
            prod_versions = client.get_latest_versions(model_name, stages=["Production"])
            if prod_versions:
                old_version = prod_versions[0]
                client.transition_model_version_stage(
                    name=model_name,
                    version=old_version.version,
                    stage="Archived"
                )
                print(f"\n📦 Ancienne version {old_version.version} archivée")
        except Exception as e:
            print(f"⚠️  Impossible d'archiver l'ancienne version: {e}")
        
        # Promouvoir en Production
        client.transition_model_version_stage(
            name=model_name,
            version=version_num,
            stage="Production"
        )
        
        print(f"\n✅ SUCCESS: Modèle v{version_num} promu en Production!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promote_model_to_production.py <model_name> [version]")
        print("Example: python promote_model_to_production.py air-quality-no2-predictor 1")
        sys.exit(1)
    
    model_name = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = promote_model(model_name, version)
    sys.exit(0 if success else 1)
