#!/bin/bash

# Configuration
AWS_REGION="eu-west-3" # Changez selon votre région
AWS_ACCOUNT_ID="118309563809" # Votre ID de compte détecté
REPO_NAME="air-quality-api"
IMAGE_TAG="latest"

echo "🚀 Démarrage du déploiement sur AWS ECR..."

# 1. Se connecter à ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 2. Builder l'image (si pas déjà fait)
docker build -t $REPO_NAME .

# 3. Tagger l'image pour AWS
docker tag $REPO_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG

# 4. Pusher l'image
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG

echo "✅ Image poussée avec succès sur ECR !"
echo "👉 Maintenant, rendez-vous sur la console AWS App Runner pour créer votre service."
