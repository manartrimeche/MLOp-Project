#!/usr/bin/env python
# scripts/test_api_prediction.py
"""
Script de test pour vérifier que l'API fonctionne correctement.
Utilisation: python scripts/test_api_prediction.py [--url http://localhost:8000]
"""

import requests
import json
import argparse
import sys
from datetime import datetime

def test_api(api_url: str = "http://localhost:8000"):
    """Test les endpoints principaux de l'API"""
    
    print("=" * 70)
    print("🧪 TEST DE L'API AIR QUALITY PREDICTION")
    print("=" * 70)
    
    success = True
    
    # Test 1: Endpoint root
    print("\n[1/5] Test GET /")
    try:
        response = requests.get(f"{api_url}/", timeout=5)
        if response.status_code == 200:
            print("  ✅ PASS")
        else:
            print(f"  ❌ FAIL: {response.status_code}")
            success = False
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        success = False
    
    # Test 2: Endpoint health
    print("\n[2/5] Test GET /health")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy" and data.get("model_loaded"):
                print("  ✅ PASS: API et modèle sain")
            else:
                print(f"  ⚠️  WARNING: {data}")
        elif response.status_code == 503:
            print("  ⚠️  WARNING: Modèle non chargé (503)")
        else:
            print(f"  ❌ FAIL: {response.status_code}")
            success = False
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        success = False
    
    # Test 3: Endpoint model-info
    print("\n[3/5] Test GET /model-info")
    try:
        response = requests.get(f"{api_url}/model-info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ PASS")
            print(f"     - Modèle: {data.get('model_name')}")
            print(f"     - Version: {data.get('model_version')}")
            print(f"     - Features: {data.get('n_features')}")
        elif response.status_code == 503:
            print("  ⚠️  WARNING: Modèle non chargé (503)")
        else:
            print(f"  ❌ FAIL: {response.status_code}")
            success = False
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        success = False
    
    # Test 4: Prédiction valide
    print("\n[4/5] Test POST /predict (données valides)")
    prediction_data = {
        "CO_GT": 2.6,
        "PT08_S1_CO": 1360.0,
        "NMHC_GT": 150.0,
        "C6H6_GT": 11.9,
        "PT08_S2_NMHC": 1046.0,
        "NOx_GT": 166.0,
        "PT08_S3_NOx": 1056.0,
        "PT08_S4_NO2": 1692.0,
        "PT08_S5_O3": 1268.0,
        "T": 13.6,
        "RH": 48.9,
        "AH": 0.7578
    }
    
    try:
        response = requests.post(
            f"{api_url}/predict",
            json=prediction_data,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            prediction = data.get("prediction")
            print(f"  ✅ PASS")
            print(f"     - Prédiction: {prediction} µg/m³")
            print(f"     - Modèle version: {data.get('model_version')}")
        elif response.status_code == 503:
            print("  ⚠️  WARNING: Modèle non chargé (503)")
        else:
            print(f"  ❌ FAIL: {response.status_code}")
            print(f"     Réponse: {response.text}")
            success = False
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        success = False
    
    # Test 5: Prédiction avec données invalides
    print("\n[5/5] Test POST /predict (données invalides)")
    invalid_data = {
        "CO_GT": 2.6
        # Données manquantes intentionnellement
    }
    
    try:
        response = requests.post(
            f"{api_url}/predict",
            json=invalid_data,
            timeout=5
        )
        if response.status_code == 422:  # Unprocessable Entity
            print("  ✅ PASS: Validation correcte (422)")
        elif response.status_code == 400:
            print("  ✅ PASS: Bad Request (400)")
        else:
            print(f"  ❌ FAIL: Code {response.status_code} (attendu 400 ou 422)")
            success = False
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        success = False
    
    # Résumé
    print("\n" + "=" * 70)
    if success:
        print("✅ TOUS LES TESTS SONT PASSÉS!")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ!")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Teste les endpoints de l'API Air Quality"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="URL de base de l'API (défaut: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    try:
        success = test_api(args.url)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur")
        sys.exit(1)
