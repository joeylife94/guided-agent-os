"""
RAG Answerer Service

Generates grounded answers using retrieved context from all RAG collections
and a local LLM.

Combines retrieved documents, builds a context-aware prompt, and calls the
local LLM to generate answers that are grounded in enterprise knowledge.
"""

from typing import Any

from app.services.local_llm import DEFAULT_LOCAL_LLM_MODEL, LocalLLMClient
from app.services.rag_document_loader import get_collection_names
from app.services.rag_retriever import retrieve_from_all_collections


DEFAULT_TOP_K = 3
MIN_TOP_K_PER_COLLECTION = 1
MAX_TOP_K_PER_COLLECTION = 10

LIMITATIONS = [
    "The answer is generated only from retrieved local knowledge base context.",
    "No real tool, SQL, or API execution was performed.",
    "For critical decisions, human review is strongly recommended.",
]


def _validate_question(question: str) -> str:
    """Normalize and validate a user question."""
    question_text = question.strip() if isinstance(question, str) else ""
    if not question_text:
        raise ValueError("Question is required.")
    return question_text


def _validate_top_k_per_collection(top_k_per_collection: int) -> int:
    """Validate the answer endpoint retrieval bound."""
    try:
        top_k = int(top_k_per_collection)
    except (TypeError, ValueError):
        raise ValueError("top_k_per_collection must be an integer.")

    if top_k < MIN_TOP_K_PER_COLLECTION or top_k > MAX_TOP_K_PER_COLLECTION:
        raise ValueError(
            "top_k_per_collection must be between "
            f"{MIN_TOP_K_PER_COLLECTION} and {MAX_TOP_K_PER_COLLECTION}."
        )
    return top_k


def _safe_score(value: Any) -> float:
    """Convert Chroma scores to JSON-serializable floats."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _safe_chunk_index(value: Any) -> int:
    """Convert chunk indexes to JSON-serializable integers."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _normalize_retrieved_context(
    retrieved_context: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    """Normalize retrieved chunks into the public response shape."""
    normalized: dict[str, list[dict[str, Any]]] = {}

    for collection_name in get_collection_names():
        normalized[collection_name] = []

        for result in retrieved_context.get(collection_name, []):
            metadata = result.get("metadata") or {}
            safe_metadata = {
                "doc_id": str(metadata.get("doc_id", "")),
                "title": str(metadata.get("title", "")),
                "source_path": str(metadata.get("source_path", "")),
                "collection": str(metadata.get("collection", collection_name)),
                "chunk_index": _safe_chunk_index(metadata.get("chunk_index", 0)),
            }

            normalized[collection_name].append({
                "content": str(result.get("content", "")),
                "metadata": safe_metadata,
                "score": _safe_score(result.get("score", 0.0)),
            })

    return normalized


def _build_context_block(retrieved_context: dict[str, list[dict[str, Any]]]) -> str:
    """
    Build a formatted context block from retrieved documents.
    
    Args:
        retrieved_context: Dict mapping collection names to lists of results
    
    Returns:
        Formatted context string for inclusion in the prompt
    """
    context_parts = []
    
    for collection_name in get_collection_names():
        results = retrieved_context.get(collection_name, [])
        if not results:
            continue
        
        collection_label = collection_name.replace("_", " ").title()
        context_parts.append(f"\n## From {collection_label}:\n")
        
        for idx, result in enumerate(results, 1):
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            title = metadata.get("title", "Unknown")
            doc_id = metadata.get("doc_id", "")
            source_path = metadata.get("source_path", "")
            chunk_index = metadata.get("chunk_index", 0)
            source_label = f"{collection_name}:{doc_id}:chunk-{chunk_index}"
            
            context_parts.append(f"\nSOURCE [{source_label}]\n")
            context_parts.append(f"Title: {title}\n")
            context_parts.append(f"Path: {source_path}\n")
            context_parts.append(f"Collection result: {idx}\n")
            context_parts.append("Content:\n")
            context_parts.append(content)
            context_parts.append("\n")
    
    if not context_parts:
        return "No relevant retrieved context was returned from the local knowledge base."

    return "".join(context_parts)


def _build_system_prompt() -> str:
    """Build the system prompt for the model."""
    return (
        "You are a controlled Guided Agent OS assistant. "
        "Your role is to answer questions using only the local retrieved "
        "knowledge base context supplied by the application. "
        "\n\n"
        "CRITICAL RULES:\n"
        "1. Answer ONLY using the provided retrieved context.\n"
        "2. Do NOT invent internal policies, database facts, APIs, tools, or capabilities.\n"
        "3. If the retrieved context is insufficient, clearly say so.\n"
        "4. Do NOT claim to have executed database queries, SQL, APIs, tools, "
        "external account actions, approvals, or file operations.\n"
        "5. Do NOT produce SQL, command, or executable code.\n"
        "6. If retrieved policy context requires human review or approval, mention it explicitly.\n"
        "7. Cite sources using only the SOURCE labels shown in the retrieved context.\n"
        "8. Keep answers concise and grounded in the retrieved knowledge."
    )


def _build_fallback_answer(
    retrieved_context: dict[str, list[dict[str, Any]]],
) -> str:
    """Build a safe deterministic answer when the local model is unavailable."""
    retrieved_count = sum(len(results) for results in retrieved_context.values())
    if retrieved_count:
        return (
            "Local LLM is unavailable, so no generated answer was produced. "
            "Retrieved local knowledge base context and source metadata are "
            "returned for caller inspection. No tool, SQL, API, or database "
            "operation was performed."
        )

    return (
        "Local LLM is unavailable, and no relevant local knowledge base context "
        "was retrieved. No tool, SQL, API, or database operation was performed."
    )


def _build_citations(
    retrieved_context: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Derive citations from retrieved chunk metadata only."""
    citations = []

    for collection_name, results in retrieved_context.items():
        for result in results:
            metadata = result.get("metadata") or {}
            citations.append({
                "doc_id": metadata.get("doc_id", ""),
                "title": metadata.get("title", ""),
                "source_path": metadata.get("source_path", ""),
                "collection": collection_name,
                "chunk_index": metadata.get("chunk_index", 0),
                "score": result.get("score", 0.0),
            })

    return citations


def generate_rag_answer(
    question: str,
    top_k_per_collection: int = DEFAULT_TOP_K,
    model: str | None = None,
    llm_client: LocalLLMClient | None = None,
) -> dict[str, Any]:
    """
    Generate a grounded answer to a question using RAG + local LLM.
    
    Args:
        question: User question to answer
        top_k_per_collection: Number of results per collection to retrieve
        model: Optional model name override
        llm_client: Optional pre-initialized LLMClient (for testing)
    
    Returns:
        Dict with:
        - question: The input question
        - answer: Generated answer or fallback message
        - citations: List of cited sources
        - retrieved_context: Dict of retrieved results by collection
        - limitations: List of limitations
        - model: Dict with provider, name, and availability
    """
    question_text = _validate_question(question)
    safe_top_k = _validate_top_k_per_collection(top_k_per_collection)

    raw_retrieved_context = retrieve_from_all_collections(
        query=question_text,
        top_k_per_collection=safe_top_k,
    )
    retrieved_context = _normalize_retrieved_context(raw_retrieved_context)
    
    # Build context block for the prompt
    context_block = _build_context_block(retrieved_context)
    
    # Initialize LLM client if not provided (for testing)
    if llm_client is None:
        llm_client = LocalLLMClient(model=model)
    
    # Try to generate answer with the local LLM
    system_prompt = _build_system_prompt()
    user_prompt = (
        f"Based on the retrieved knowledge base context below, "
        f"answer the following question:\n\n"
        f"QUESTION: {question_text}\n\n"
        f"RETRIEVED CONTEXT:\n{context_block}\n\n"
        f"Answer only from the retrieved context. If the context is insufficient, "
        f"say that it is insufficient.\n\n"
        f"ANSWER:"
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    
    try:
        llm_response = llm_client.chat(messages=messages, temperature=0.2)
    except Exception as e:
        llm_response = {
            "ok": False,
            "model": getattr(llm_client, "model", model or DEFAULT_LOCAL_LLM_MODEL),
            "content": "",
            "error": f"Unexpected local LLM client error: {str(e)}",
        }
    
    citations = _build_citations(retrieved_context)
    
    # Determine model availability
    model_name = (
        llm_response.get("model")
        or getattr(llm_client, "model", None)
        or model
        or DEFAULT_LOCAL_LLM_MODEL
    )
    llm_content = str(llm_response.get("content", "")).strip()
    model_available = bool(llm_response.get("ok", False) and llm_content)
    
    # Build answer based on LLM availability
    if model_available:
        answer = llm_content
    else:
        answer = _build_fallback_answer(retrieved_context)
        if llm_response.get("ok", False) and not llm_content:
            llm_response["error"] = "Local LLM returned an empty response."
    
    return {
        "question": question_text,
        "answer": answer,
        "citations": citations,
        "retrieved_context": retrieved_context,
        "limitations": LIMITATIONS,
        "model": {
            "provider": "local",
            "name": model_name,
            "available": model_available,
        },
        "error": llm_response.get("error") if not model_available else None,
    }
