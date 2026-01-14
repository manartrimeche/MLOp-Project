# Simulation de Déploiement et Rollback

Ce document décrit comment simuler une mise à jour de version (v1 → v2) et un rollback en cas de problème.

## 1. Déploiement Initial (v1)

Le déploiement initial est effectué en utilisant l'image tagguée `v1`.

```bash
# Construire l'image v1
docker build -t air-quality-api:v1 .

# Lancer avec docker-compose
# Modifier docker-compose.yml pour utiliser air-quality-api:v1
docker-compose up -d
```

## 2. Mise à jour vers v2

Une fois qu'un nouveau modèle est prêt (ex: après un run ZenML ou Optuna), nous créons une nouvelle image `v2`.

```bash
# Construire l'image v2
docker build -t air-quality-api:v2 .

# Mettre à jour le service
# Modifier docker-compose.yml pour utiliser air-quality-api:v2
docker-compose up -d
```

## 3. Rollback vers v1

Si la version `v2` présente des anomalies (ex: latence élevée, erreurs 500), nous pouvons rapidement revenir à la version `v1`.

```bash
# Revenir à l'image v1 dans docker-compose.yml
# Puis relancer
docker-compose up -d
```

## 4. Preuve de Reproductibilité

Le versioning est assuré par :
- **Git** : Code source taggué `v1` et `v2`.
- **DVC** : Données trackées par `.dvc`.
- **ZenML/MLflow** : Pipeline et artefacts de modèle tracés.
