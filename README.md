# telaria-embeddings

Microservice **Python d'embeddings**, composant du socle IA de Codexia (Lot 0 —
cœur RAG). Dépôt **autonome** (aucun PHP), déployable séparément. Consommé en
**HTTP** par le bundle « cœur RAG » Symfony.

- **Stack** : FastAPI + sentence-transformers + uvicorn.
- **Modèle** : `intfloat/multilingual-e5-base` (multilingue FR, léger CPU), chargé
  **une seule fois** au démarrage.
- **Stateless**, bind **`127.0.0.1`** (jamais exposé publiquement).
- Préfixes e5 (`query: ` / `passage: `) gérés **côté service** ; `normalize_embeddings=True`.

> Contrat HTTP = source de vérité : `codexia-doc/specs/ia-coeur.md` §4.1.

## Contrat HTTP

```
GET  /health  → { "status": "ok", "model": "intfloat/multilingual-e5-base", "dim": 768 }

POST /embed
  requête : { "type": "query"|"passage", "texts": ["..."] }
  réponse : { "model": "intfloat/multilingual-e5-base", "dim": 768, "vectors": [[...], ...] }
```

`type` est validé strictement (`query` ou `passage`, sinon `422`) ; `texts` doit
être non vide. Un vecteur est renvoyé par texte, dans l'ordre.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Le modèle est téléchargé au premier lancement (accès réseau requis, ~1,1 Go).

## Lancement

```bash
uvicorn app:app --host 127.0.0.1 --port 8001
```

L'URL est injectée côté Symfony via `rag.embedding.service_url`.

## Test rapide (curl)

```bash
curl http://127.0.0.1:8001/health

curl -X POST http://127.0.0.1:8001/embed \
  -H "Content-Type: application/json" \
  -d '{"type":"passage","texts":["Comment réinitialiser mon mot de passe ?"]}'
```

## Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt

pytest            # tests rapides (modèle mocké, pas de téléchargement)
pytest -m slow    # test d'intégration : charge le VRAI modèle (lent, réseau)
```

Les tests rapides mockent le modèle (`tests/fakes.py`) via `app.dependency_overrides`
→ pas de téléchargement, exécution en CI possible. Ils vérifient la forme du
contrat, l'application des préfixes e5 et la validation des entrées.

## Déploiement (VPS CPU-only, systemd)

Cible confirmée : VPS Linux, **Python 3.13.2** (cf. `.python-version`), 12 Go RAM,
disque suffisant (le modèle pèse ~1,1 Go). Procédure générale ci-dessous ;
`codexia-doc/guides/deployment.md` fait foi côté infra.

**1. Prérequis système** (python3 n'est pas préinstallé sur le VPS) :

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
```

**2. Code + venv** (déployé dans `/opt/telaria-embeddings`) :

```bash
sudo install -d -o telaria -g telaria /opt/telaria-embeddings
# (déployer le contenu du dépôt dans /opt/telaria-embeddings, puis :)
cd /opt/telaria-embeddings
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
# Lock reproductible, généré SUR LA CIBLE (Linux/3.13) puis commité dans le dépôt :
.venv/bin/pip freeze > requirements.lock
```

> **`requirements.lock`** : non versionné depuis un poste Windows (les wheels, ex. `torch`,
> sont spécifiques à la plateforme/version). Il se génère sur le VPS (Linux/3.13.2) et se
> commite ensuite, pour des installations ultérieures via `pip install -r requirements.lock`.

**3. Cache du modèle sur disque** (jamais `/tmp` = tmpfs/RAM). Pré-cache **optionnel**
mais recommandé (évite ~1,1 Go au 1er boot) :

```bash
sudo install -d -o telaria -g telaria /var/lib/telaria-embeddings/hf
sudo -u telaria HF_HOME=/var/lib/telaria-embeddings/hf \
  /opt/telaria-embeddings/.venv/bin/python -c \
  "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-base')"
```

**4. Service systemd** — l'unité est versionnée dans `deploy/telaria-embeddings.service`
(bind `127.0.0.1:8001`, `HF_HOME` sur disque, durcissement) :

```bash
sudo cp deploy/telaria-embeddings.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now telaria-embeddings
```

Surveiller la **mémoire** (un seul modèle chargé). `/health` sert à la supervision
(interrogé par la commande `app:rag:stats` côté Symfony) ; au 1er boot sans pré-cache,
`/health` n'est prêt qu'après le téléchargement du modèle.

## Lancer via Docker (dev local, parité WSL2)

Le dépôt fournit son image (`Dockerfile` + `compose.yaml`). Le conteneur écoute
`0.0.0.0:8001` **en interne** ; le port n'est publié que sur `127.0.0.1:8001` de
l'hôte (pas d'exposition publique). Le healthcheck interroge `/health` via `curl`.

```bash
docker compose up -d
curl http://127.0.0.1:8001/health     # {"status":"ok","model":"...","dim":768}
```

Le volume `hf-cache` (monté sur `/home/app/.cache/huggingface`) persiste le modèle
(~1,1 Go) entre deux `up`. Côté `codexia`, le `compose.yaml` de dev référence
`ghcr.io/<owner>/telaria-embeddings:latest` (ou `build: ../telaria-embeddings`).

**Publier l'image sur GHCR** (action manuelle ou CI ; nécessite Docker + login) :

```bash
docker build -t ghcr.io/<owner>/telaria-embeddings:0.1.x .
echo "$GHCR_TOKEN" | docker login ghcr.io -u mathieuadrien --password-stdin
docker push ghcr.io/<owner>/telaria-embeddings:0.1.x
```

## Conventions Git

Conventions canon : `codexia-doc/guides/git-conventions.md` (s'applique aux 3 dépôts).

- **Branches (GitFlow solo + IA)** : on travaille sur `develop` ; `master` reçoit les
  releases via **merge direct `--ff-only`, sans PR**. `master` n'est **pas** protégée
  (choix assumé ; à activer si une équipe ou une CI rejoint).
- **Messages** : Conventional Commits (`type(scope): sujet`), trailer `Co-Authored-By`
  pour les commits assistés par IA.
- **Normalisation** : LF + UTF-8 imposés par `.gitattributes`.
- **Hook `pre-push`** : rejoue `pytest` (tests rapides) avant chaque push. Activation
  **une fois** par clone :
  ```bash
  git config core.hooksPath scripts/hooks
  ```

## Périmètre

V1 = ce microservice (`/health`, `/embed`) + tests + `requirements.txt` + README.
**Hors périmètre** : côté Symfony, index `sqlite-vec` (autres lots).
