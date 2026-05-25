"""Test d'intégration : charge le VRAI modèle e5-base.

Lourd (~1,1 Go au 1er run, réseau requis). Désactivé par défaut.
Lancer explicitement :  pytest -m slow
"""

import pytest
from fastapi.testclient import TestClient

import app as service
from app import app

pytestmark = pytest.mark.slow


def test_real_model_end_to_end():
    # `with` → déclenche le lifespan → chargement réel du modèle.
    with TestClient(app) as client:
        health = client.get("/health").json()
        assert health == {"status": "ok", "model": service.MODEL_NAME, "dim": 768}

        res = client.post("/embed", json={"type": "query", "texts": ["mot de passe oublié"]})
        body = res.json()
        assert body["dim"] == 768
        assert len(body["vectors"]) == 1
        vec = body["vectors"][0]
        assert len(vec) == 768
        # normalize_embeddings=True → norme L2 ≈ 1.
        norm = sum(x * x for x in vec) ** 0.5
        assert abs(norm - 1.0) < 1e-3
