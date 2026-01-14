.PHONY: help install install-dev test test-cov lint format clean docker-build docker-up docker-down train api api-reload promote-model test-api docs mlflow

PYTHON := python
PIP := pip
PROJECT_NAME := air-quality-api

# ============================================================================
# Aide
# ============================================================================
help:
	@echo "================================"
	@echo "$(PROJECT_NAME) - Makefile"
	@echo "================================"
	@echo ""
	@echo "Installation et Setup:"
	@echo "  make install          - Installer les dépendances"
	@echo "  make install-dev      - Installer les dépendances dev"
	@echo "  make setup            - Setup complet (install + .env)"
	@echo ""
	@echo "Développement:"
	@echo "  make train            - Entraîner le modèle"
	@echo "  make api              - Démarrer l'API (production)"
	@echo "  make api-reload       - Démarrer l'API (dev avec reload)"
	@echo "  make test             - Exécuter les tests"
	@echo "  make test-cov         - Tests avec couverture"
	@echo "  make lint             - Vérifier la qualité du code"
	@echo "  make format           - Formater le code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     - Build les images Docker"
	@echo "  make docker-up        - Démarrer les containers"
	@echo "  make docker-down      - Arrêter les containers"
	@echo "  make docker-logs      - Afficher les logs"
	@echo ""
	@echo "Production:"
	@echo "  make promote-model    - Promouvoir le modèle en Production"
	@echo "  make test-api         - Tester l'API (doit être running)"
	@echo ""
	@echo "Utilitaires:"
	@echo "  make mlflow           - Démarrer MLflow UI"
	@echo "  make docs             - Ouvrir la documentation API"
	@echo "  make clean            - Nettoyer les fichiers temporaires"
	@echo ""

# ============================================================================
# Installation
# ============================================================================
install:
	@echo "📦 Installation des dépendances..."
	$(PIP) install -r requirements.txt

install-dev:
	@echo "📦 Installation des dépendances de développement..."
	$(PIP) install -r requirements-dev.txt

setup: install
	@echo "⚙️  Configuration du projet..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Fichier .env créé"; \
	fi
	@echo "✅ Setup complété!"

# ============================================================================
# Développement
# ============================================================================
train:
	@echo "🤖 Entraînement du modèle..."
	$(PYTHON) src/train_final_model.py

api:
	@echo "🚀 Démarrage de l'API (production)..."
	$(PYTHON) -m uvicorn src.api:app --host 0.0.0.0 --port 8000

api-reload:
	@echo "🚀 Démarrage de l'API (développement)..."
	$(PYTHON) -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "🧪 Exécution des tests..."
	$(PYTHON) -m pytest tests/ -v

test-cov:
	@echo "📊 Tests avec couverture..."
	$(PYTHON) -m pytest tests/ --cov=src --cov-report=html --cov-report=term -v
	@echo "✅ Rapport HTML: htmlcov/index.html"

lint:
	@echo "🔍 Vérification de la qualité du code..."
	@echo "  - flake8..."
	-flake8 src/ tests/ --max-line-length=100
	@echo "  - black..."
	-black --check src/ tests/
	@echo "  - isort..."
	-isort --check-only src/ tests/

format:
	@echo "✨ Formatage du code..."
	@echo "  - isort..."
	isort src/ tests/
	@echo "  - black..."
	black src/ tests/
	@echo "✅ Code formaté!"

# ============================================================================
# Docker
# ============================================================================
docker-build:
	@echo "🐳 Build des images Docker..."
	docker-compose build

docker-up:
	@echo "🐳 Démarrage des containers..."
	docker-compose up -d
	@echo "⏳ Attendre 30-40 secondes pour MLflow..."
	@echo "✅ Services démarrés!"
	@echo "   - API: http://localhost:8000"
	@echo "   - MLflow: http://localhost:5000"

docker-down:
	@echo "🛑 Arrêt des containers..."
	docker-compose down

docker-logs:
	@echo "📋 Logs des containers..."
	docker-compose logs -f

# ============================================================================
# Production
# ============================================================================
promote-model:
	@echo "📤 Promotion du modèle en Production..."
	$(PYTHON) scripts/promote_model_to_production.py air-quality-no2-predictor

test-api:
	@echo "🧪 Test de l'API..."
	@echo "⚠️  L'API doit être running (http://localhost:8000)"
	$(PYTHON) scripts/test_api_prediction.py

# ============================================================================
# Utilitaires
# ============================================================================
mlflow:
	@echo "📊 Démarrage de MLflow UI..."
	mlflow ui --port 5000
	@echo "✅ MLflow: http://localhost:5000"

docs:
	@echo "📖 Ouverture de la documentation API..."
	@echo "Swagger: http://localhost:8000/docs"
	@echo "ReDoc: http://localhost:8000/redoc"
	@echo "Guide complet: docs/api_guide.md"

clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf .pytest_cache/ 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	rm -rf .mypy_cache/ 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info 2>/dev/null || true
	@echo "✅ Nettoyage complété!"

# ============================================================================
# Workflow complet
# ============================================================================
.PHONY: workflow-dev workflow-docker

workflow-dev: clean install setup train api-reload
	@echo "✅ Workflow développement lancé!"

workflow-docker: clean install docker-build docker-up test-api
	@echo "✅ Workflow Docker lancé!"

# ============================================================================
# Default
# ============================================================================
.DEFAULT_GOAL := help
