# Script PowerShell pour lancer Streamlit
# Usage: .\streamlit.ps1

Write-Host "🎨 Lancement de Streamlit..." -ForegroundColor Green

# Vérifier si l'environnement virtuel est activé
if ($null -eq $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Activation de l'environnement virtuel..." -ForegroundColor Yellow
    & ".\\.venv\Scripts\Activate.ps1"
}

# Vérifier si Streamlit est installé
Write-Host "🔍 Vérification de Streamlit..." -ForegroundColor Cyan
python -m pip show streamlit | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "📦 Installation de Streamlit..." -ForegroundColor Yellow
    python -m pip install streamlit plotly -q
}

# Vérifier si l'API est lancée
Write-Host "🔍 Vérification de l'API..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API lancée et fonctionnelle" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  ATTENTION: L'API n'est pas lancée!" -ForegroundColor Yellow
    Write-Host "   Lancez dans un autre terminal:" -ForegroundColor Yellow
    Write-Host "   .\.venv\Scripts\python -m uvicorn src.api:app --reload --host 127.0.0.1 --port 8000" -ForegroundColor Yellow
}

# Lancer Streamlit
Write-Host "`n✅ Lancement de Streamlit sur http://localhost:8501" -ForegroundColor Green
Write-Host "   (L'application s'ouvrira automatiquement)" -ForegroundColor Gray
Write-Host "   Appuyez sur Ctrl+C pour arrêter`n" -ForegroundColor Gray

.\.venv\Scripts\streamlit run app.py
