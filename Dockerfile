# syntax=docker/dockerfile:1
# Image du microservice telaria-embeddings (consommée par le compose de dev de
# codexia : service `embeddings`, cf. codexia-doc/guides/install-locale.md §5).
FROM python:3.13-slim

# curl : requis par le healthcheck docker-compose (test sur /health).
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Utilisateur non-root `app` (home /home/app). Le cache Hugging Face atterrit
# par défaut dans /home/app/.cache/huggingface → c'est là que le compose monte
# le volume `hf-cache` (persiste le modèle ~1,1 Go entre deux `up`).
RUN useradd --create-home --home-dir /home/app --shell /usr/sbin/nologin app \
 && mkdir -p /home/app/.cache/huggingface \
 && chown -R app:app /home/app/.cache

WORKDIR /app

# Dépendances d'abord (cache de build), puis le code applicatif.
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY app.py ./

USER app
EXPOSE 8001

# 1er démarrage : téléchargement du modèle au préchargement (lifespan) → laisser
# le temps avant de considérer le conteneur « unhealthy ».
HEALTHCHECK --interval=10s --timeout=3s --retries=5 --start-period=300s \
  CMD curl -fsS http://127.0.0.1:8001/health || exit 1

# Bind 0.0.0.0 DANS le conteneur : la frontière d'isolation est le conteneur,
# l'exposition « locale » est assurée par la publication 127.0.0.1:8001 côté hôte
# (cf. compose.yaml). Jamais d'exposition publique.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
