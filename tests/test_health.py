"""GET /health — forme du contrat (ia-coeur.md §4.1)."""

import app as service


def test_health_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {
        "status": "ok",
        "model": service.MODEL_NAME,
        "dim": 768,
    }
