"""
RAG Retriever Service

Queries ChromaDB collections to retrieve relevant documents.
Supports querying single collections or all collections at once.
"""

from typing import Dict, List, Any

from app.services.rag_indexer import (
    get_chroma_client,
)
from app.services.rag_document_loader import get_collection_names
from app.services.rag_embeddings import embed_texts


MIN_TOP_K = 1
MAX_TOP_K = 20


def _normalize_result(
    content: str,
    metadata: Dict[str, Any],
    score: float,
) -> Dict[str, Any]:
    """
    Normalize a retrieved result to standard format.
    
    Args:
        content: Document chunk text
        metadata: Metadata dict
        score: Similarity score
    
    Returns:
        Normalized result dict
    """
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
    """Clamp top_k to the safe service-level retrieval bounds."""
    try:
        requested_top_k = int(top_k)
    except (TypeError, ValueError):
        requested_top_k = default

    if requested_top_k < MIN_TOP_K:
        return MIN_TOP_K
    return min(requested_top_k, MAX_TOP_K)


def retrieve_from_collection(
    query: str,
    collection_name: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Query a specific ChromaDB collection.
    
    Args:
        query: Query text to search for
        collection_name: Name of collection to query
        top_k: Number of top results to return
    
    Returns:
        List of normalized result dicts, sorted by score (highest first)
        Each dict contains: content, metadata, score
    """
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
    
    try:
        results = collection.query(
            query_embeddings=embed_texts([query_text]),
            n_results=safe_top_k,
            include=["documents", "metadatas", "distances"],
        )
    except Exception:
        return []
    
    # Normalize results
    normalized = []
    
    if not results or not results.get("documents"):
        return []
    
    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []
    
    # ChromaDB returns distances, convert to similarity scores (0-1 range)
    # Using cosine similarity: score = 1 - distance
    for doc, meta, distance in zip(documents, metadatas, distances):
        score = max(0, min(1, 1 - distance))
        normalized.append(_normalize_result(doc, meta, score))
    
    # Sort by score descending
    normalized.sort(key=lambda x: x["score"], reverse=True)
    
    return normalized


def retrieve_from_all_collections(
    query: str,
    top_k_per_collection: int = 3,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Query all collections.
    
    Args:
        query: Query text to search for
        top_k_per_collection: Number of top results per collection
    
    Returns:
        Dict mapping collection names to lists of normalized results
        Example:
        {
            "domain_knowledge": [...],
            "agent_policy": [...],
            "tool_catalog": [...],
        }
    """
    if not query or not query.strip():
        return {collection_name: [] for collection_name in get_collection_names()}

    safe_top_k = normalize_top_k(top_k_per_collection, default=3)
    results = {}
    
    for collection_name in get_collection_names():
        results[collection_name] = retrieve_from_collection(
            query=query.strip(),
            collection_name=collection_name,
            top_k=safe_top_k,
        )
    
    return results


def search_all_collections(
    query: str,
    top_k_per_collection: int = 3,
) -> List[Dict[str, Any]]:
    """
    Search all collections and return results as a flat list.
    
    Results are sorted by score across all collections.
    
    Args:
        query: Query text to search for
        top_k_per_collection: Number of results per collection
    
    Returns:
        Flat list of normalized results sorted by score
    """
    all_results = retrieve_from_all_collections(
        query=query,
        top_k_per_collection=top_k_per_collection,
    )
    
    # Flatten results
    flat = []
    for results in all_results.values():
        flat.extend(results)
    
    # Sort by score descending
    flat.sort(key=lambda x: x["score"], reverse=True)
    
    return flat
