# Changelog

Toutes les modifications notables de `telaria-embeddings` sont consignées ici.

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) ;
versionnage [SemVer](https://semver.org/lang/fr/). Branches : GitFlow solo
(cf. `codexia-doc/guides/releases.md`).

## [Unreleased]

## [0.1.2] - 2026-05-28

### Ajouté
- Image Docker (`Dockerfile`, `.dockerignore`, `compose.yaml`) pour le dev local
  WSL2 (parité VPS) : `python:3.13-slim`, user non-root `app`, bind `0.0.0.0:8001`
  publié sur `127.0.0.1:8001`, healthcheck `/health`, volume de cache HF monté sur
  `/home/app/.cache/huggingface`.
- Workflow GitHub Actions `docker-publish` : build & push de l'image sur GHCR
  (`ghcr.io/mathieuadrien/telaria-embeddings`) à chaque tag `v*.*.*` (+ `latest`)
  et à chaque push sur `develop` (tag `develop`). Cache de build GHA.
- `requirements.lock` (CPU-only) versionné — généré sur le VPS sous Python 3.13.2,
  reproductible (zéro paquet CUDA/NVIDIA/triton).

### Modifié
- `requirements.txt` : épingle `torch==2.12.0+cpu` + `--extra-index-url` du wheel
  CPU PyTorch. Évite de tirer ~plusieurs Go de pile NVIDIA/CUDA sur une cible
  CPU-only (constaté lors du 1er déploiement VPS 2026-05-26).
- README : section Docker (lancement `compose`, publication GHCR).

## [0.1.1] - 2026-05-26

### Ajouté
- `deploy/telaria-embeddings.service` : unité systemd versionnée (bind `127.0.0.1:8001`,
  `HF_HOME` sur disque, durcissement, `TimeoutStartSec` pour le 1er téléchargement).
- `.python-version` : `3.13.2` (version cible confirmée du VPS).

### Modifié
- README : procédure de déploiement détaillée (prérequis `apt`, venv, pré-cache du
  modèle, `requirements.lock` généré sur la cible, installation systemd).

## [0.1.0] - 2026-05-26

Première version du microservice Python d'embeddings (Lot 0 — cœur RAG).

### Ajouté
- Service FastAPI conforme au contrat `codexia-doc/specs/ia-coeur.md` §4.1 :
  - `GET /health` → `{ "status": "ok", "model": …, "dim": 768 }`.
  - `POST /embed` → req `{ "type": "query"|"passage", "texts": [...] }`,
    res `{ "model": …, "dim": 768, "vectors": [[...], ...] }`.
- Modèle `intfloat/multilingual-e5-base` chargé une seule fois au démarrage
  (`lifespan` + `lru_cache`), service stateless.
- Préfixes e5 (`query: ` / `passage: `) gérés côté service ; `normalize_embeddings=True`.
- Validation stricte des entrées (`type` ∈ {query, passage}, `texts` non vide) → `422`
  (acté avec l'équipe doc, `ia-coeur.md` §4.1 / §10).
- Tests : suite rapide à modèle mocké + test d'intégration `slow` (vrai modèle).
- `requirements.txt` (runtime figé) et `requirements-dev.txt`.
- README (installation, lancement `127.0.0.1:8001`, contrat, tests, unité systemd).
- Conventions Git : `.gitattributes` (LF/UTF-8) et hook `pre-push` (pytest).

[Unreleased]: https://github.com/mathieuadrien/telaria-embeddings/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/mathieuadrien/telaria-embeddings/releases/tag/v0.1.2
[0.1.1]: https://github.com/mathieuadrien/telaria-embeddings/releases/tag/v0.1.1
[0.1.0]: https://github.com/mathieuadrien/telaria-embeddings/releases/tag/v0.1.0
