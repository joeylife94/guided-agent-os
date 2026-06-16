"""
RAG Indexer Service

Manages ChromaDB indexing with persistent storage and local embeddings.
Creates and maintains three knowledge collections for the RAG system.
"""

import os
from pathlib import Path
from typing import Dict, List, Any
import chromadb
from chromadb.config import Settings

from app.services.rag_embeddings import EMBEDDING_DIMENSIONS, embed_texts
from app.services.rag_document_loader import (
    load_and_chunk_documents,
    get_collection_names,
)


def get_chroma_db_path() -> str:
    """
    Get or create the ChromaDB storage directory.
    
    Creates ./data/chroma if it doesn't exist.
    
    Returns:
        Absolute path to chroma database directory
    """
    configured_path = os.getenv("RAG_CHROMA_PATH")
    if configured_path:
        data_dir = Path(configured_path)
    else:
        base_dir = Path(__file__).parent.parent.parent  # project root
        data_dir = base_dir / "data" / "chroma"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir)


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Get or create a persistent ChromaDB client.
    
    Uses persistent local storage. Embeddings are supplied explicitly by the
    indexing and retrieval services.
    
    Returns:
        ChromaDB PersistentClient instance
    """
    db_path = get_chroma_db_path()
    
    settings = Settings(
        is_persistent=True,
        persist_directory=db_path,
        anonymized_telemetry=False,
    )
    
    client = chromadb.PersistentClient(
        path=db_path,
        settings=settings,
    )
    
    return client


def _get_or_create_collections(
    client: chromadb.PersistentClient,
) -> Dict[str, Any]:
    """
    Get or create the three knowledge collections.
    
    Returns:
        Dict mapping collection name to collection object
    """
    collections = {}
    
    for collection_name in get_collection_names():
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={
                "hnsw:space": "cosine",
                "embedding": "deterministic_local_hash_v1",
                "embedding_dimensions": EMBEDDING_DIMENSIONS,
            },
        )
        collections[collection_name] = collection
    
    return collections


def _reset_collections(client: chromadb.PersistentClient) -> Dict[str, Any]:
    """
    Recreate the managed RAG collections before a rebuild.

    This keeps rebuilds idempotent and removes stale chunks if a Markdown file
    is deleted or chunk boundaries change.
    """
    for collection_name in get_collection_names():
        try:
            client.delete_collection(name=collection_name)
        except Exception:
            pass

    return _get_or_create_collections(client)


def rebuild_rag_index() -> Dict[str, Any]:
    """
    Rebuild the RAG index by loading documents and indexing them in ChromaDB.
    
    Loads all markdown documents from the knowledge directory,
    chunks them, embeds them using deterministic local embeddings,
    and stores them in ChromaDB collections.
    
    Returns:
        Summary dict with status and collection statistics
        Example:
        {
            "status": "indexed",
            "collections": {
                "domain_knowledge": 10,
                "agent_policy": 8,
                "tool_catalog": 7,
            }
        }
    """
    # Reset the managed collections so rebuilds never accumulate duplicate or
    # stale chunks.
    client = get_chroma_client()
    collections = _reset_collections(client)
    
    # Load and chunk all documents
    chunks = load_and_chunk_documents()
    
    # Group chunks by collection
    chunks_by_collection: Dict[str, List[Dict]] = {}
    for collection_name in get_collection_names():
        chunks_by_collection[collection_name] = []
    
    for chunk in chunks:
        collection_name = chunk["metadata"]["collection"]
        chunks_by_collection[collection_name].append(chunk)
    
    # Index chunks into their respective collections
    collection_stats = {}
    
    for collection_name, collection_chunks in chunks_by_collection.items():
        if not collection_chunks:
            collection_stats[collection_name] = 0
            continue
        
        collection = collections[collection_name]
        
        # Prepare data for indexing
        ids = [chunk["doc_id"] for chunk in collection_chunks]
        documents = [chunk["content"] for chunk in collection_chunks]
        metadatas = [chunk["metadata"] for chunk in collection_chunks]
        
        embeddings = embed_texts(documents)

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
    }


def get_collection_count(collection_name: str) -> int:
    """
    Get the number of items in a collection.
    
    Args:
        collection_name: Name of the collection
    
    Returns:
        Number of documents in the collection
    """
    if collection_name not in get_collection_names():
        return 0

    client = get_chroma_client()
    
    try:
        collection = client.get_collection(name=collection_name)
        return collection.count()
    except Exception:
        return 0


def get_index_stats() -> Dict[str, Any]:
    """
    Get current index statistics without rebuilding.
    
    Returns:
        Dict with collection counts
    """
    stats = {}
    for collection_name in get_collection_names():
        stats[collection_name] = get_collection_count(collection_name)
    
    return stats
