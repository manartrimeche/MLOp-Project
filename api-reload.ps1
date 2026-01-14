# Script pour démarrer l'API en mode développement
Write-Host "🚀 Démarrage de l'API (mode développement)..." -ForegroundColor Cyan
Write-Host "📖 Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
