# Configuration
$AWS_REGION = "eu-west-3" # Changez selon votre région
$AWS_ACCOUNT_ID = "118309563809" # Votre ID de compte détecté
$REPO_NAME = "air-quality-api"
$IMAGE_TAG = "latest"

# 1. Vérifier si AWS CLI est dans le PATH, sinon utiliser le chemin par défaut
$AWS_EXE = "aws"
if (-not (Get-Command "aws" -ErrorAction SilentlyContinue)) {
    $DefaultPath = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
    if (Test-Path $DefaultPath) {
        $AWS_EXE = "& '$DefaultPath'"
        Write-Host "ℹ️ AWS CLI trouvé dans le chemin par défaut : $DefaultPath" -ForegroundColor Gray
    } else {
        Write-Error "❌ Impossible de trouver 'aws.exe'. Veuillez l'installer ou l'ajouter au PATH."
        exit 1
    }
}

Write-Host "🚀 Démarrage du déploiement sur AWS ECR..." -ForegroundColor Cyan

# 1. Se connecter à ECR
$LoginPassword = Invoke-Expression "$AWS_EXE ecr get-login-password --region $AWS_REGION"
$LoginPassword | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# 2. Builder l'image
docker build -t $REPO_NAME .

# 3. Tagger l'image pour AWS
docker tag "$REPO_NAME:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG"

# 4. Pusher l'image
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG"

Write-Host "✅ Image poussée avec succès sur ECR !" -ForegroundColor Green
Write-Host "👉 Maintenant, rendez-vous sur la console AWS App Runner pour créer votre service." -ForegroundColor Yellow
