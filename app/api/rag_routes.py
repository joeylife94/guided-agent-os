"""
RAG API Routes

FastAPI endpoints for rebuilding and querying the RAG system.
Provides access to the multi-collection knowledge base and RAG answer generation.
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List

from app.services.rag_indexer import rebuild_rag_index
from app.services.rag_retriever import (
    MAX_TOP_K,
    retrieve_from_collection,
    retrieve_from_all_collections,
)
from app.services.rag_document_loader import get_collection_names
from app.services.rag_answerer import generate_rag_answer


router = APIRouter(prefix="/api/rag", tags=["rag"])


# ============================================================================
# Pydantic Models for RAG Answer endpoint
# ============================================================================

class RAGAnswerRequest(BaseModel):
    """Request body for RAG answer generation."""
    question: str = Field(
        ...,
        description="Question to answer using the knowledge base",
        min_length=1,
        examples=["How should an AI agent handle legacy database access?"],
    )
    top_k_per_collection: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of results to retrieve per collection",
    )
    model: Optional[str] = Field(
        default=None,
        description="Optional model name override",
    )

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        """Reject whitespace-only questions before retrieval or LLM calls."""
        question = value.strip()
        if not question:
            raise ValueError("Question is required.")
        return question

    @field_validator("model")
    @classmethod
    def blank_model_is_default(cls, value: Optional[str]) -> Optional[str]:
        """Treat blank model overrides the same as an omitted model."""
        if value is None:
            return None

        model = value.strip()
        return model or None


class CitationModel(BaseModel):
    """Citation information for a retrieved document."""
    doc_id: str
    title: str
    source_path: str
    collection: str
    chunk_index: int
    score: float


class ModelMetadata(BaseModel):
    """Metadata about the LLM used for generation."""
    provider: str
    name: str
    available: bool


class RetrievedContextEntry(BaseModel):
    """A single retrieved context entry."""
    content: str
    metadata: Dict[str, Any]
    score: float


class RAGAnswerResponse(BaseModel):
    """Response body for RAG answer generation."""
    question: str
    answer: str
    citations: List[CitationModel]
    retrieved_context: Dict[str, List[RetrievedContextEntry]]
    limitations: List[str]
    model: ModelMetadata
    error: Optional[str] = None


# ============================================================================
# Endpoints


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


@router.post("/answer", response_model=RAGAnswerResponse)
async def answer_question(request: RAGAnswerRequest) -> Dict[str, Any]:
    """
    Generate a grounded answer using RAG + local LLM.

    Retrieves relevant context from all knowledge base collections,
    builds a grounded prompt, calls the local LLM, and returns a structured answer
    with citations, retrieved context, and model metadata.

    Request body:
    - question: Question to answer (required)
    - top_k_per_collection: Results per collection (1-10, default: 3)
    - model: Optional model name override

    Response:
    - answer: Generated answer or fallback message
    - citations: List of sources used
    - retrieved_context: Raw retrieved documents by collection
    - limitations: Known limitations of the answer
    - model: Metadata about the LLM used
    - error: Error message if model was unavailable

    Example:
    {
        "question": "How should an AI agent handle legacy database access?",
        "top_k_per_collection": 2
    }
    """
    try:
        result = generate_rag_answer(
            question=request.question,
            top_k_per_collection=request.top_k_per_collection,
            model=request.model,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )

