"""
RAG API Routes

FastAPI endpoints for rebuilding and querying the RAG system.
Provides access to the multi-collection knowledge base.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any

from app.services.rag_indexer import rebuild_rag_index
from app.services.rag_retriever import (
    MAX_TOP_K,
    retrieve_from_collection,
    retrieve_from_all_collections,
)
from app.services.rag_document_loader import get_collection_names


router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/rebuild-index")
async def rebuild_index() -> Dict[str, Any]:
    """
    Rebuild the ChromaDB index from local Markdown documents.
    
    Loads all documents from app/knowledge/, chunks them,
    and indexes them into ChromaDB collections.
    
    Returns:
        Dict with status and collection statistics
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
    try:
        result = rebuild_rag_index()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error rebuilding index: {str(e)}"
        )


@router.get("/query")
async def query_collection(
    q: str = Query(..., description="Query text"),
    collection: str = Query("domain_knowledge", description="Collection name"),
    top_k: int = Query(5, ge=1, le=MAX_TOP_K, description="Number of results to return"),
) -> Dict[str, Any]:
    """
    Query a specific collection.
    
    Query parameters:
    - q: Search query text (required)
    - collection: Collection name (default: "domain_knowledge")
    - top_k: Number of top results (default: 5, max: 20)
    
    Returns:
        Dict with results list
        Example:
        {
            "query": "Should the agent execute database changes?",
            "collection": "agent_policy",
            "results": [
                {
                    "content": "...",
                    "metadata": {
                        "doc_id": "...",
                        "title": "...",
                        "source_path": "...",
                        "collection": "agent_policy",
                        "chunk_index": 0
                    },
                    "score": 0.92
                }
            ]
        }
    """
    valid_collections = get_collection_names()
    
    if collection not in valid_collections:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid collection. Valid options: {valid_collections}"
        )
    
    query_text = q.strip() if q else ""
    if not query_text:
        raise HTTPException(
            status_code=400,
            detail="Query text (q) is required"
        )
    
    try:
        results = retrieve_from_collection(
            query=query_text,
            collection_name=collection,
            top_k=top_k,
        )
        
        return {
            "query": query_text,
            "collection": collection,
            "results": results,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying collection: {str(e)}"
        )


@router.get("/query-all")
async def query_all_collections(
    q: str = Query(..., description="Query text"),
    top_k: int = Query(3, ge=1, le=MAX_TOP_K, description="Number of results per collection"),
) -> Dict[str, Any]:
    """
    Query all collections.
    
    Query parameters:
    - q: Search query text (required)
    - top_k: Number of results per collection (default: 3, max: 20)
    
    Returns:
        Dict mapping collection names to results
        Example:
        {
            "query": "legacy database access",
            "results": {
                "domain_knowledge": [...],
                "agent_policy": [...],
                "tool_catalog": [...]
            }
        }
    """
    query_text = q.strip() if q else ""
    if not query_text:
        raise HTTPException(
            status_code=400,
            detail="Query text (q) is required"
        )
    
    try:
        results = retrieve_from_all_collections(
            query=query_text,
            top_k_per_collection=top_k,
        )
        
        return {
            "query": query_text,
            "results": results,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying collections: {str(e)}"
        )


