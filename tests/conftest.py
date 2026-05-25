"""Fixtures partagées : client de test avec modèle mocké.

L'override de `get_model` est posé par fixture (et nettoyé après chaque test)
pour éviter que les modules de test se marchent dessus via le global
`app.dependency_overrides`.
"""

import pytest
from fastapi.testclient import TestClient

from app import app, get_model
from tests.fakes import FakeModel


@pytest.fixture
def fake() -> FakeModel:
    return FakeModel()


@pytest.fixture
def client(fake: FakeModel) -> TestClient:
    app.dependency_overrides[get_model] = lambda: fake
    # Pas de context manager → lifespan non déclenché → pas de modèle réel.
    yield TestClient(app)
    app.dependency_overrides.clear()
