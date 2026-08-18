from __future__ import annotations

import pytest

from app.services import rag_embeddings


@pytest.fixture(autouse=True)
def clear_provider_cache():
    rag_embeddings.get_embedding_provider.cache_clear()
    yield
    rag_embeddings.get_embedding_provider.cache_clear()


def test_hash_provider_requires_explicit_selection():
    provider = rag_embeddings.get_embedding_provider(provider_name="hash_test")

    assert provider.name == "hash_test"
    assert provider.dimensions == 64
    assert len(provider.embed_texts(["legacy database access"])[0]) == 64


def test_default_provider_is_bge_m3(monkeypatch):
    monkeypatch.delenv("RAG_EMBEDDING_PROVIDER", raising=False)
    monkeypatch.delenv("RAG_EMBEDDING_MODEL", raising=False)

    provider = rag_embeddings.get_embedding_provider()

    assert provider.name == "bge_m3"
    assert provider.model_name == "BAAI/bge-m3"


def test_unsupported_provider_fails_clearly():
    with pytest.raises(RuntimeError, match="Unsupported RAG_EMBEDDING_PROVIDER"):
        rag_embeddings.get_embedding_provider(provider_name="unknown")


def test_semantic_provider_does_not_fallback_when_dependency_missing(monkeypatch):
    provider = rag_embeddings.SentenceTransformerEmbeddingProvider("BAAI/bge-m3")

    original_import = __import__

    def blocking_import(name, *args, **kwargs):
        if name == "sentence_transformers":
            raise ImportError("blocked for test")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", blocking_import)

    with pytest.raises(RuntimeError, match="no hash fallback"):
        provider.embed_texts(["test"])


def test_embedding_metadata_reports_explicit_hash_test_provider():
    provider = rag_embeddings.get_embedding_provider(provider_name="hash_test")

    metadata = rag_embeddings.get_embedding_metadata(provider)

    assert metadata == {
        "embedding_provider": "hash_test",
        "embedding_model": "deterministic_local_hash_v1",
        "embedding_dimensions": 64,
    }
