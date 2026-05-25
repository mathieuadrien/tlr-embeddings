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

Le service tourne en tâche de fond dans son venv. Exemple d'unité
`/etc/systemd/system/telaria-embeddings.service` :

```ini
[Unit]
Description=telaria-embeddings (microservice d'embeddings)
After=network.target

[Service]
User=telaria
WorkingDirectory=/opt/telaria-embeddings
ExecStart=/opt/telaria-embeddings/.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8001
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now telaria-embeddings
```

Surveiller la **mémoire** (un seul modèle chargé). `/health` sert à la supervision
(interrogé par la commande `app:rag:stats` côté Symfony).

## Périmètre

V1 = ce microservice (`/health`, `/embed`) + tests + `requirements.txt` + README.
**Hors périmètre** : côté Symfony, index `sqlite-vec` (autres lots).
