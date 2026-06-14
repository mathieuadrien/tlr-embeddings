# Instructions Claude — tlr-embeddings

> Consignes projet : voir [`AGENTS.md`](AGENTS.md).

## Mon rôle dans l'équipe

- **Dépôt** : `tlr-embeddings`
- **Rôle** : Service owner — microservice Python `/embed` `/health` (FastAPI, multilingual-e5-base)
- **Modèle** : `claude-sonnet-4-6` (versionné dans `.claude/settings.json`)
- **Autorité technique** : Lead dev `telaria-app` (dernier mot).
- **Autorité processus / coordination** : `telaria-doc` / Atlas.

## À lire au démarrage

1. [`AGENTS.md`](AGENTS.md) — règles éditoriales.
2. `C:\src\telaria-doc\pilotage\ecosystem.md` — registre de l'écosystème.
3. `C:\src\telaria-doc\pilotage\telaria-style.md` — coding style (§8 Python/FastAPI).

## Spec faisant foi

`C:\src\telaria-doc\02-ce-que-je-construis\specs\ia-coeur.md` (contrat HTTP `/embed`).

## Anti-patterns

- Trancher unilatéralement un point inter-instances.
- Modifier le contrat HTTP sans validation `telaria-doc`.
- Monter en gamme de modèle sans décision Mathieu.
