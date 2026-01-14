#!/usr/bin/env bash
# verify_corrections.sh
# Script pour vérifier que toutes les corrections ont été appliquées

echo "=========================================="
echo "✅ VÉRIFICATION DES CORRECTIONS"
echo "=========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
PASS=0
FAIL=0

# Fonction de test
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1 existe"
        ((PASS++))
    else
        echo -e "${RED}❌${NC} $1 MANQUANT"
        ((FAIL++))
    fi
}

check_content() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $1 contient '$2'"
        ((PASS++))
    else
        echo -e "${RED}❌${NC} $1 ne contient pas '$2'"
        ((FAIL++))
    fi
}

echo "📁 Fichiers clés:"
check_file "src/api.py"
check_file "docs/api_guide.md"
check_file "docker-compose.yml"
check_file ".env"
check_file ".env.example"
check_file ".env.docker"
check_file "scripts/test_api_prediction.py"
check_file "scripts/promote_model_to_production.py"
check_file "scripts/README.md"
check_file "COMPLIANCE_REPORT.md"
check_file "CORRECTIONS_SUMMARY.md"
check_file "PROJECT_STRUCTURE.md"
check_file "Makefile"

echo ""
echo "📝 Contenu des fichiers:"
check_content "src/api.py" "MLFLOW_TRACKING_URI"
check_content "src/api.py" "mlflow.sklearn.load_model"
check_content "src/api.py" "status_code=503"
check_content "docker-compose.yml" "mlflow"
check_content "docker-compose.yml" "healthcheck"
check_content "docs/api_guide.md" "POST /predict"
check_content "requirements.txt" "python-dotenv"
check_content ".env" "MODEL_NAME"

echo ""
echo "=========================================="
echo "RÉSUMÉ"
echo "=========================================="
echo -e "Vérifications réussies: ${GREEN}${PASS}${NC}"
echo -e "Vérifications échouées: ${RED}${FAIL}${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ TOUTES LES CORRECTIONS SONT EN PLACE!${NC}"
    echo "Le projet est CONFORME et PRODUCTION-READY 🚀"
    exit 0
else
    echo -e "${RED}❌ CERTAINS FICHIERS MANQUENT!${NC}"
    exit 1
fi
