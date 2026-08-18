"""
RAG Indexer Service

Manages ChromaDB indexing with persistent storage and an explicit embedding
provider boundary. Index metadata records the exact provider/model/dimension so
retrieval can reject incompatible indexes instead of failing silently.
"""

import os
from pathlib import Path
from typing import Dict, List, Any
import chromadb
from chromadb.config import Settings

from app.services.rag_embeddings import (
    embed_texts,
    get_embedding_metadata,
    get_embedding_provider,
)
from app.services.rag_document_loader import (
    load_and_chunk_documents,
    get_collection_names,
)


def get_chroma_db_path() -> str:
    """Get or create the ChromaDB storage directory."""
    configured_path = os.getenv("RAG_CHROMA_PATH")
    if configured_path:
        data_dir = Path(configured_path)
    else:
        base_dir = Path(__file__).parent.parent.parent
        data_dir = base_dir / "data" / "chroma"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir)


def get_chroma_client() -> chromadb.PersistentClient:
    """Get or create a persistent ChromaDB client."""
    db_path = get_chroma_db_path()
    settings = Settings(
        is_persistent=True,
        persist_directory=db_path,
        anonymized_telemetry=False,
    )
    return chromadb.PersistentClient(path=db_path, settings=settings)


def _get_or_create_collections(
    client: chromadb.PersistentClient,
    embedding_metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Get or create the managed collections with embedding metadata."""
    metadata = embedding_metadata or get_embedding_metadata()
    collection_metadata = {
        "hnsw:space": "cosine",
        **metadata,
    }
    collections = {}
    for collection_name in get_collection_names():
        collections[collection_name] = client.get_or_create_collection(
            name=collection_name,
            metadata=collection_metadata,
        )
    return collections


def _reset_collections(
    client: chromadb.PersistentClient,
    embedding_metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """Recreate managed collections before a rebuild."""
    for collection_name in get_collection_names():
        try:
            client.delete_collection(name=collection_name)
        except Exception:
            pass
    return _get_or_create_collections(client, embedding_metadata)


def rebuild_rag_index() -> Dict[str, Any]:
    """Rebuild the RAG index with one configured embedding provider."""
    provider = get_embedding_provider()
    embedding_metadata = get_embedding_metadata(provider)

    client = get_chroma_client()
    collections = _reset_collections(client, embedding_metadata)
    chunks = load_and_chunk_documents()

    chunks_by_collection: Dict[str, List[Dict]] = {
        collection_name: [] for collection_name in get_collection_names()
    }
    for chunk in chunks:
        collection_name = chunk["metadata"]["collection"]
        chunks_by_collection[collection_name].append(chunk)

    collection_stats = {}
    for collection_name, collection_chunks in chunks_by_collection.items():
        if not collection_chunks:
            collection_stats[collection_name] = 0
            continue

        collection = collections[collection_name]
        ids = [chunk["doc_id"] for chunk in collection_chunks]
        documents = [chunk["content"] for chunk in collection_chunks]
        metadatas = [chunk["metadata"] for chunk in collection_chunks]
        embeddings = embed_texts(documents, provider=provider)

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        collection_stats[collection_name] = len(collection_chunks)

    return {
        "status": "indexed",
        "collections": collection_stats,
        "embedding": embedding_metadata,
    }


def get_collection_count(collection_name: str) -> int:
    """Get the number of items in a collection."""
    if collection_name not in get_collection_names():
        return 0

    client = get_chroma_client()
    try:
        collection = client.get_collection(name=collection_name)
        return collection.count()
    except Exception:
        return 0


def get_index_stats() -> Dict[str, Any]:
    """Get current collection counts without rebuilding."""
    return {
        collection_name: get_collection_count(collection_name)
        for collection_name in get_collection_names()
    }
