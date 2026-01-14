# 💻 Guide pour Windows PowerShell

Puisque `make` n'est pas disponible sur Windows, utilisez les scripts PowerShell fournis.

## 📋 Scripts disponibles

### 1. Installation des dépendances
```powershell
.\install.ps1
```

### 2. Configuration du projet
```powershell
# Créer et activer le virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Puis installer les dépendances
.\install.ps1

# Configurer .env (optionnel, déjà créé)
# cp .env.example .env
```

### 3. Entraîner le modèle
```powershell
.\train.ps1
```

### 4. Démarrer l'API
```powershell
.\api-reload.ps1
```

### 5. Tester l'API (dans un autre terminal)
```powershell
.\test-api.ps1
```

---

## 🚀 Workflow complet (développement local)

```powershell
# Terminal 1 - Setup
.\install.ps1
.\train.ps1

# Terminal 1 - Démarrer l'API
.\api-reload.ps1

# Terminal 2 - Tester
.\test-api.ps1
```

---

## 🐳 Pour Docker (production)

```powershell
# Démarrer tous les services
docker-compose up -d

# Attendre 30-40 secondes
Start-Sleep -Seconds 40

# Tester l'API
.\test-api.ps1
```

---

## 🛠️ Commandes manuelles (sans scripts)

Si les scripts ne fonctionnent pas, utilisez ces commandes directes:

```powershell
# Installation
pip install -r requirements.txt

# Entraînement
python src/train_final_model.py

# API
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

# Tests
python scripts/test_api_prediction.py

# Tests unitaires
python -m pytest tests/ -v

# Linting
flake8 src/ tests/
black --check src/ tests/
isort --check-only src/ tests/
```

---

## ⚙️ Configuration requise

- Python 3.11+
- Virtual environment activé (`.\.venv\Scripts\Activate.ps1`)
- Dépendances installées (`pip install -r requirements.txt`)

---

## 🔧 Installation de Make sur Windows (optionnel)

Si vous voulez utiliser `make`, installez-le via Chocolatey:

```powershell
# Avec Chocolatey
choco install make

# Ou avec Scoop
scoop install make

# Ou télécharger GnuWin32
# https://gnuwin32.sourceforge.net/packages/make.htm
```

Après installation, vous pouvez utiliser:
```powershell
make install
make train
make api-reload
make test-api
```

---

## 📚 Documentation

- [docs/api_guide.md](docs/api_guide.md) - Guide API complet
- [QUICK_SUMMARY.md](QUICK_SUMMARY.md) - Synthèse des corrections
- [INDEX.md](INDEX.md) - Index de la documentation

---

## ❓ Troubleshooting

### "activate.ps1 cannot be loaded because running scripts is disabled"

```powershell
# Autoriser l'exécution des scripts pour la session actuelle
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Puis activer le venv
.\.venv\Scripts\Activate.ps1
```

### "python: command not found"

```powershell
# Vérifier que Python est installé
python --version

# Ou utiliser python.exe explicitement
python.exe -m pip install -r requirements.txt
python.exe src/train_final_model.py
```

### "pip: command not found"

```powershell
# Utiliser le module pip directement
python -m pip install -r requirements.txt
```

---

## ✅ Vérification

Pour vérifier que tout fonctionne:

```powershell
# Vérifier Python
python --version

# Vérifier les dépendances
pip list | grep -E "mlflow|fastapi|pandas|scikit-learn"

# Vérifier les fichiers importants
Test-Path "src/api.py"
Test-Path "models/feature_names.json"
Test-Path "mlflow.db"
```

---

**Dernière mise à jour**: Janvier 10, 2026
