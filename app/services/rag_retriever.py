"""
RAG Retriever Service

Queries ChromaDB collections using the same configured embedding provider that
created the index. Provider/model/dimension mismatches fail explicitly and
require an index rebuild; retrieval never silently falls back to hash vectors.
"""

from typing import Dict, List, Any

from app.services.rag_indexer import get_chroma_client
from app.services.rag_document_loader import get_collection_names
from app.services.rag_embeddings import (
    embed_texts,
    get_embedding_metadata,
    get_embedding_provider,
)


MIN_TOP_K = 1
MAX_TOP_K = 20


def _normalize_result(
    content: str,
    metadata: Dict[str, Any],
    score: float,
) -> Dict[str, Any]:
    return {
        "content": content,
        "metadata": {
            "doc_id": metadata.get("doc_id", ""),
            "title": metadata.get("title", ""),
            "source_path": metadata.get("source_path", ""),
            "collection": metadata.get("collection", ""),
            "chunk_index": metadata.get("chunk_index", 0),
        },
        "score": score,
    }


def normalize_top_k(top_k: int, default: int = 5) -> int:
    """Clamp top_k to safe retrieval bounds."""
    try:
        requested_top_k = int(top_k)
    except (TypeError, ValueError):
        requested_top_k = default

    if requested_top_k < MIN_TOP_K:
        return MIN_TOP_K
    return min(requested_top_k, MAX_TOP_K)


def _assert_embedding_compatible(
    collection: Any,
    expected: Dict[str, Any],
) -> None:
    """Reject stale indexes built with a different embedding configuration."""
    metadata = collection.metadata or {}
    keys = ("embedding_provider", "embedding_model", "embedding_dimensions")
    mismatches = {
        key: (metadata.get(key), expected.get(key))
        for key in keys
        if metadata.get(key) != expected.get(key)
    }
    if mismatches:
        raise RuntimeError(
            "RAG index embedding configuration does not match the active provider. "
            f"Mismatches: {mismatches}. Rebuild the RAG index before querying."
        )


def retrieve_from_collection(
    query: str,
    collection_name: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Query a specific ChromaDB collection."""
    if not query or not query.strip():
        return []
    if collection_name not in get_collection_names():
        return []

    query_text = query.strip()
    safe_top_k = normalize_top_k(top_k, default=5)
    client = get_chroma_client()

    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        return []

    provider = get_embedding_provider()
    expected_metadata = get_embedding_metadata(provider)
    _assert_embedding_compatible(collection, expected_metadata)

    try:
        results = collection.query(
            query_embeddings=embed_texts([query_text], provider=provider),
            n_results=safe_top_k,
            include=["documents", "metadatas", "distances"],
        )
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(
            f"RAG query failed for collection '{collection_name}': {exc}"
        ) from exc

    if not results or not results.get("documents"):
        return []

    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []

    normalized = []
    for doc, meta, distance in zip(documents, metadatas, distances):
        score = max(0, min(1, 1 - distance))
        normalized.append(_normalize_result(doc, meta, score))
    normalized.sort(key=lambda x: x["score"], reverse=True)
    return normalized


def retrieve_from_all_collections(
    query: str,
    top_k_per_collection: int = 3,
) -> Dict[str, List[Dict[str, Any]]]:
    """Query all managed collections."""
    if not query or not query.strip():
        return {collection_name: [] for collection_name in get_collection_names()}

    safe_top_k = normalize_top_k(top_k_per_collection, default=3)
    return {
        collection_name: retrieve_from_collection(
            query=query.strip(),
            collection_name=collection_name,
            top_k=safe_top_k,
        )
        for collection_name in get_collection_names()
    }


def search_all_collections(
    query: str,
    top_k_per_collection: int = 3,
) -> List[Dict[str, Any]]:
    """Search all collections and return one score-sorted list."""
    all_results = retrieve_from_all_collections(
        query=query,
        top_k_per_collection=top_k_per_collection,
    )
    flat = []
    for results in all_results.values():
        flat.extend(results)
    flat.sort(key=lambda x: x["score"], reverse=True)
    return flat
