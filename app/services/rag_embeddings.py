"""
Deterministic local embeddings for the Phase 1 RAG index.

The Phase 1 RAG engine must not depend on OpenAI, cloud APIs, or heavyweight
model downloads. This module provides a small hashed bag-of-words embedding
that is stable across runs and adequate for local indexing tests.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Iterable, List


EMBEDDING_DIMENSIONS = 64
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def embed_text(text: str) -> List[float]:
    """Return a deterministic normalized embedding for a single text."""
    vector = [0.0] * EMBEDDING_DIMENSIONS
    normalized_text = text.lower()
    tokens = _TOKEN_PATTERN.findall(normalized_text)

    if not tokens and normalized_text.strip():
        tokens = [normalized_text.strip()]

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for offset in range(0, len(digest), 2):
            index = digest[offset] % EMBEDDING_DIMENSIONS
            sign = 1.0 if digest[offset + 1] % 2 == 0 else -1.0
            weight = 1.0 + (digest[offset + 1] % 7) / 7.0
            vector[index] += sign * weight

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector

    return [value / norm for value in vector]


def embed_texts(texts: Iterable[str]) -> List[List[float]]:
    """Return deterministic normalized embeddings for multiple texts."""
    return [embed_text(text) for text in texts]
