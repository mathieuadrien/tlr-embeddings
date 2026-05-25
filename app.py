"""telaria-embeddings — microservice d'embeddings (socle IA Codexia).

Contrat HTTP : source de vérité = codexia-doc/specs/ia-coeur.md §4.1.
Service stateless. Modèle chargé une seule fois au démarrage. Bind 127.0.0.1.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any, Literal

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

MODEL_NAME = "intfloat/multilingual-e5-base"

# Convention e5 : préfixes gérés CÔTÉ SERVICE selon `type` (ia-coeur.md §3.3).
# Le client Symfony n'a pas à s'en soucier.
_PREFIX = {"query": "query: ", "passage": "passage: "}


@lru_cache(maxsize=1)
def get_model() -> Any:
    """Charge le modèle UNE SEULE FOIS (mémoïsé pour toute la durée de vie).

    Import paresseux : importer `sentence_transformers` (et torch) au niveau
    module rendrait les tests mockés dépendants de libs lourdes. Ici, seul le
    démarrage réel du service paie ce coût.
    """
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Préchargement au démarrage (et non à la première requête).
    get_model()
    yield


app = FastAPI(title="telaria-embeddings", lifespan=lifespan)


class EmbedRequest(BaseModel):
    type: Literal["query", "passage"]
    texts: list[str] = Field(..., min_length=1)


class EmbedResponse(BaseModel):
    model: str
    dim: int
    vectors: list[list[float]]


class HealthResponse(BaseModel):
    status: str
    model: str
    dim: int


@app.get("/health", response_model=HealthResponse)
def health(model: Any = Depends(get_model)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        model=MODEL_NAME,
        dim=model.get_sentence_embedding_dimension(),
    )


@app.post("/embed", response_model=EmbedResponse)
def embed(
    req: EmbedRequest,
    model: Any = Depends(get_model),
) -> EmbedResponse:
    # Préfixe e5 selon l'usage, puis normalisation L2 (similarité cosinus).
    inputs = [_PREFIX[req.type] + t for t in req.texts]
    vectors = model.encode(inputs, normalize_embeddings=True).tolist()
    return EmbedResponse(
        model=MODEL_NAME,
        dim=model.get_sentence_embedding_dimension(),
        vectors=vectors,
    )
