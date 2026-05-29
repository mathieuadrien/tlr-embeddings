"""POST /embed — contrat (ia-coeur.md §4.1) : forme, préfixes e5, validation."""

import app as service
from tests.fakes import DIM


def test_embed_response_shape(client):
    res = client.post("/embed", json={"type": "passage", "texts": ["bonjour", "salut le monde"]})
    assert res.status_code == 200
    body = res.json()
    assert body["model"] == service.MODEL_NAME
    assert body["dim"] == 768
    assert len(body["vectors"]) == 2
    assert all(len(v) == DIM for v in body["vectors"])


def test_embed_applies_passage_prefix(client, fake):
    client.post("/embed", json={"type": "passage", "texts": ["abc"]})
    assert fake.last_inputs == ["passage: abc"]


def test_embed_applies_query_prefix(client, fake):
    client.post("/embed", json={"type": "query", "texts": ["abc"]})
    assert fake.last_inputs == ["query: abc"]


def test_embed_normalizes_for_cosine(client, fake):
    client.post("/embed", json={"type": "query", "texts": ["abc"]})
    assert fake.last_normalize is True


def test_embed_rejects_invalid_type(client):
    res = client.post("/embed", json={"type": "document", "texts": ["abc"]})
    assert res.status_code == 422


def test_embed_rejects_empty_texts(client):
    res = client.post("/embed", json={"type": "query", "texts": []})
    assert res.status_code == 422


def test_embed_rejects_empty_string_item(client):
    res = client.post("/embed", json={"type": "query", "texts": ["", "abc"]})
    assert res.status_code == 422
