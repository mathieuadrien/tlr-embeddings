# Changelog

Toutes les modifications notables de `telaria-embeddings` sont consignées ici.

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) ;
versionnage [SemVer](https://semver.org/lang/fr/). Branches : GitFlow solo
(cf. `codexia-doc/guides/releases.md`).

## [Unreleased]

### Ajouté
- `deploy/telaria-embeddings.service` : unité systemd versionnée (bind `127.0.0.1:8001`,
  `HF_HOME` sur disque, durcissement, `TimeoutStartSec` pour le 1er téléchargement).
- `.python-version` : `3.13.2` (version cible confirmée du VPS).
- Image Docker (`Dockerfile`, `.dockerignore`, `compose.yaml`) pour le dev local
  WSL2 (parité VPS) : `python:3.13-slim`, user non-root `app`, bind `0.0.0.0:8001`
  publié sur `127.0.0.1:8001`, healthcheck `/health`, volume de cache HF.
  ⚠️ Non encore buildée/testée (Docker indisponible sur le poste de dev Windows) ;
  à valider en WSL2 avant publication GHCR.

### Modifié
- README : procédure de déploiement détaillée (prérequis `apt`, venv, pré-cache du
  modèle, `requirements.lock` généré sur la cible, installation systemd) + section Docker.

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

[Unreleased]: https://github.com/mathieuadrien/telaria-embeddings/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mathieuadrien/telaria-embeddings/releases/tag/v0.1.0
