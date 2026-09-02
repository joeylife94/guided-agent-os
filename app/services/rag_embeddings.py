"""Embedding provider boundary for the Guided Agent OS RAG index.

Proof v1.0 defaults to a real local multilingual semantic embedding model.
The deterministic hash provider remains available only when it is explicitly
selected for tests; production/runtime configuration never silently falls back
from the semantic provider to the hash implementation.
"""

from __future__ import annotations

import hashlib
import math
import os
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, List, Protocol


DEFAULT_PROVIDER = "sentence_transformers"
DEFAULT_SENTENCE_TRANSFORMERS_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LEGACY_BGE_PROVIDER_ALIAS = "bge_m3"
HASH_TEST_PROVIDER = "hash_test"
HASH_TEST_DIMENSIONS = 64
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class EmbeddingProvider(Protocol):
    """Minimal contract shared by indexing and retrieval."""

    name: str
    model_name: str
    dimensions: int

    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        """Embed one or more texts using one stable provider/model."""


@dataclass
class HashTestEmbeddingProvider:
    """Deterministic provider reserved for explicit test configuration."""

    name: str = HASH_TEST_PROVIDER
    model_name: str = "deterministic_local_hash_v1"
    dimensions: int = HASH_TEST_DIMENSIONS

    def _embed_text(self, text: str) -> List[float]:
        vector = [0.0] * self.dimensions
        normalized_text = text.lower()
        tokens = _TOKEN_PATTERN.findall(normalized_text)

        if not tokens and normalized_text.strip():
            tokens = [normalized_text.strip()]

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for offset in range(0, len(digest), 2):
                index = digest[offset] % self.dimensions
                sign = 1.0 if digest[offset + 1] % 2 == 0 else -1.0
                weight = 1.0 + (digest[offset + 1] % 7) / 7.0
                vector[index] += sign * weight

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        return [self._embed_text(text) for text in texts]


class SentenceTransformerEmbeddingProvider:
    """Lazy local SentenceTransformers provider for semantic embeddings."""

    def __init__(self, model_name: str) -> None:
        self.name = DEFAULT_PROVIDER
        self.model_name = model_name
        self._model = None
        self.dimensions = 0

    def _load_model(self):
        if self._model is not None:
            return self._model

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "Semantic RAG requires the 'sentence-transformers' dependency. "
                "Install requirements.txt; no hash fallback is used."
            ) from exc

        try:
            model = SentenceTransformer(self.model_name)
        except Exception as exc:
            raise RuntimeError(
                f"Unable to load semantic embedding model '{self.model_name}'. "
                "Ensure the model is available locally or model downloads are permitted. "
                "No hash fallback is used."
            ) from exc

        dimensions = model.get_sentence_embedding_dimension()
        if not dimensions:
            raise RuntimeError(
                f"Embedding model '{self.model_name}' did not report a valid dimension."
            )

        self._model = model
        self.dimensions = int(dimensions)
        return model

    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        values = list(texts)
        if not values:
            return []

        model = self._load_model()
        encoded = model.encode(values, normalize_embeddings=True)
        return [vector.tolist() for vector in encoded]


@lru_cache(maxsize=None)
def get_embedding_provider(
    provider_name: str | None = None,
    model_name: str | None = None,
) -> EmbeddingProvider:
    """Return the configured provider without implicit fallback behavior.

    ``bge_m3`` remains an explicit compatibility alias for callers that already
    select it, but the implementation boundary and persisted provider metadata
    truthfully identify SentenceTransformers.
    """
    selected = (provider_name or os.getenv("RAG_EMBEDDING_PROVIDER", DEFAULT_PROVIDER)).strip().lower()

    if selected == HASH_TEST_PROVIDER:
        return HashTestEmbeddingProvider()

    if selected in {DEFAULT_PROVIDER, LEGACY_BGE_PROVIDER_ALIAS}:
        configured_model = (
            model_name
            or os.getenv("RAG_EMBEDDING_MODEL", DEFAULT_SENTENCE_TRANSFORMERS_MODEL)
        ).strip()
        if not configured_model:
            raise RuntimeError(
                "RAG_EMBEDDING_MODEL must not be empty for sentence_transformers provider."
            )
        return SentenceTransformerEmbeddingProvider(configured_model)

    raise RuntimeError(
        f"Unsupported RAG_EMBEDDING_PROVIDER '{selected}'. "
        f"Supported providers: {DEFAULT_PROVIDER}, {LEGACY_BGE_PROVIDER_ALIAS}, {HASH_TEST_PROVIDER}."
    )


def get_embedding_metadata(provider: EmbeddingProvider | None = None) -> dict[str, str | int]:
    """Return collection metadata for the active provider.

    Semantic providers are loaded here so the embedding dimension is known
    before a collection is created. Configuration/model failures therefore
    fail the index rebuild clearly instead of creating a partial index.
    """
    active = provider or get_embedding_provider()
    if active.dimensions <= 0:
        active.embed_texts(["embedding dimension probe"])

    return {
        "embedding_provider": active.name,
        "embedding_model": active.model_name,
        "embedding_dimensions": int(active.dimensions),
    }


def embed_texts(
    texts: Iterable[str],
    provider: EmbeddingProvider | None = None,
) -> List[List[float]]:
    """Embed texts through the configured provider boundary."""
    active = provider or get_embedding_provider()
    return active.embed_texts(texts)
