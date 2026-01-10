import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import numpy as np
from src.api import app


client = TestClient(app)


def test_root():
    """Test de la route racine"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["status"] == "running"


@patch('src.api.model')
def test_health_check_with_model(mock_model):
    """Test du health check quand le modèle est chargé"""
    with patch('src.api.model', Mock()):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_health_check_without_model():
    """Test du health check quand le modèle n'est pas chargé"""
    with patch('src.api.model', None):
        response = client.get("/health")
        assert response.status_code == 503
        assert "Modèle non chargé" in response.json()["detail"]


@patch('src.api.model')
def test_predict_success(mock_model):
    """Test de prédiction réussie"""
    mock_instance = Mock()
    mock_instance.predict.return_value = np.array([90.83])
    
    with patch('src.api.model', mock_instance):
        data = {
            "CO_GT": 2.6,
            "NMHC_GT": 150.0,
            "C6H6_GT": 11.9,
            "NOx_GT": 113.0,
            "PT08_S1_CO": 1360.0,
            "PT08_S2_NMHC": 1046.0,
            "PT08_S3_NOx": 166.0,
            "PT08_S4_NO2": 1056.0,
            "PT08_S5_O3": 1692.0,
            "T": 13.6,
            "RH": 48.9,
            "AH": 0.7578
        }
        
        response = client.post("/predict", json=data)
        assert response.status_code == 200
        result = response.json()
        
        # Accepter les deux formats de réponse
        assert ("prediction" in result or "prediction_NO2_GT" in result)
        assert ("model_version" in result or "model_info" in result)
        
        # Vérifier que la prédiction est un nombre
        prediction_value = result.get("prediction") or result.get("prediction_NO2_GT")
        assert isinstance(prediction_value, float)


def test_predict_invalid_data():
    """Test avec données invalides (type incorrect)"""
    data = {"CO_GT": "invalid"}
    response = client.post("/predict", json=data)
    assert response.status_code == 422


def test_predict_missing_fields():
    """Test avec champs manquants"""
    data = {"CO_GT": 2.6}
    response = client.post("/predict", json=data)
    assert response.status_code == 422


@patch('src.api.model')
def test_predict_batch(mock_model):
    """Test de prédiction batch"""
    mock_instance = Mock()
    mock_instance.predict.return_value = np.array([90.83, 85.42])
    
    with patch('src.api.model', mock_instance):
        data = [
            {
                "CO_GT": 2.6,
                "NMHC_GT": 150.0,
                "C6H6_GT": 11.9,
                "NOx_GT": 113.0,
                "PT08_S1_CO": 1360.0,
                "PT08_S2_NMHC": 1046.0,
                "PT08_S3_NOx": 166.0,
                "PT08_S4_NO2": 1056.0,
                "PT08_S5_O3": 1692.0,
                "T": 13.6,
                "RH": 48.9,
                "AH": 0.7578
            },
            {
                "CO_GT": 2.0,
                "NMHC_GT": 120.0,
                "C6H6_GT": 9.5,
                "NOx_GT": 100.0,
                "PT08_S1_CO": 1200.0,
                "PT08_S2_NMHC": 950.0,
                "PT08_S3_NOx": 150.0,
                "PT08_S4_NO2": 1000.0,
                "PT08_S5_O3": 1600.0,
                "T": 15.0,
                "RH": 45.0,
                "AH": 0.8
            }
        ]
        
        response = client.post("/predict/batch", json=data)
        assert response.status_code == 200
        result = response.json()
        assert "predictions" in result
        assert "count" in result
        assert result["count"] == 2
        assert len(result["predictions"]) == 2


def test_predict_without_model():
    """Test de prédiction quand le modèle n'est pas disponible"""
    with patch('src.api.model', None):
        data = {
            "CO_GT": 2.6,
            "NMHC_GT": 150.0,
            "C6H6_GT": 11.9,
            "NOx_GT": 113.0,
            "PT08_S1_CO": 1360.0,
            "PT08_S2_NMHC": 1046.0,
            "PT08_S3_NOx": 166.0,
            "PT08_S4_NO2": 1056.0,
            "PT08_S5_O3": 1692.0,
            "T": 13.6,
            "RH": 48.9,
            "AH": 0.7578
        }
        response = client.post("/predict", json=data)
        assert response.status_code == 503
        assert "Modèle non disponible" in response.json()["detail"]


@patch('src.api.model')
def test_predict_exception(mock_model):
    """Test de gestion d'erreur lors de la prédiction"""
    mock_instance = Mock()
    mock_instance.predict.side_effect = Exception("Erreur de prédiction")
    
    with patch('src.api.model', mock_instance):
        data = {
            "CO_GT": 2.6,
            "NMHC_GT": 150.0,
            "C6H6_GT": 11.9,
            "NOx_GT": 113.0,
            "PT08_S1_CO": 1360.0,
            "PT08_S2_NMHC": 1046.0,
            "PT08_S3_NOx": 166.0,
            "PT08_S4_NO2": 1056.0,
            "PT08_S5_O3": 1692.0,
            "T": 13.6,
            "RH": 48.9,
            "AH": 0.7578
        }
        response = client.post("/predict", json=data)
        assert response.status_code == 500
        assert "Erreur de prédiction" in response.json()["detail"]
