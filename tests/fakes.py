"""Faux encodeur pour les tests : évite de télécharger ~1,1 Go (e5-base).

Reproduit l'interface de SentenceTransformer utilisée par le service :
- get_sentence_embedding_dimension() -> int
- encode(inputs, normalize_embeddings=bool) -> np.ndarray (.tolist())
"""

from __future__ import annotations

import numpy as np

DIM = 768


class FakeModel:
    def __init__(self) -> None:
        # Mémorise le dernier appel pour vérifier les préfixes e5 côté test.
        self.last_inputs: list[str] | None = None
        self.last_normalize: bool | None = None

    def get_sentence_embedding_dimension(self) -> int:
        return DIM

    def encode(self, inputs, normalize_embeddings: bool = False):
        self.last_inputs = list(inputs)
        self.last_normalize = normalize_embeddings
        # Vecteurs déterministes (valeur = longueur du texte), shape (n, DIM).
        return np.array([[float(len(t))] * DIM for t in inputs], dtype=np.float32)
