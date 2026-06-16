"""
Tool/API Execution Plan Generator

Generates a deterministic, rule-based execution plan for tool/API calls
without actually executing anything.

This is a critical safety component: the LLM does not directly call tools,
execute SQL, or invoke APIs. Instead, it generates a structured plan that
outlines what WOULD be executed, which is then routed to human review if needed.
"""

from __future__ import annotations

from typing import Any


def _infer_requires_approval(risk_level: str) -> bool:
    """Check if a risk level requires approval."""
    high_risk = {"internal", "restricted", "high", "critical", "sensitive"}
    return str(risk_level).strip().lower() in high_risk if risk_level else False


def _detect_system_access_risk(user_request: str, normalized_data: dict) -> bool:
    """Detect if request implies system/DB/API access."""
    request_lower = user_request.lower()
    
    # Keywords that suggest system access
    system_keywords = [
        "database", "db", "query", "sql", "table", "record", "data",
        "api", "endpoint", "service", "legacy", "system", "backend", "tool",
        "integration", "connector",
        "internal", "fetch", "retrieve", "lookup", "search", "access",
        "execute", "run", "call", "invoke", "trigger", "sync",
    ]
    
    for keyword in system_keywords:
        if keyword in request_lower:
            return True
    
    # Check normalized data for system-related fields
    data_sources = normalized_data.get("data_sources", [])
    if isinstance(data_sources, str):
        data_sources = [data_sources]

    if isinstance(data_sources, list):
        system_source_keywords = [
            "database",
            "db",
            "api",
            "legacy",
            "backend",
            "internal",
            "system",
        ]
        for source in [str(s).lower() for s in data_sources]:
            if any(keyword in source for keyword in system_source_keywords):
                return True
    
    return False


def _detect_rag_insufficient(rag_answer: dict) -> bool:
    """Check if RAG answer suggests the context is insufficient."""
    answer_text = rag_answer.get("answer", "").lower() if rag_answer else ""
    
    insufficient_indicators = [
        "insufficient",
        "not found",
        "no relevant",
        "unable to",
        "cannot find",
        "requires human",
        "requires approval",
    ]
    
    for indicator in insufficient_indicators:
        if indicator in answer_text:
            return True
    
    return False


def generate_tool_plan(
    user_request: str,
    normalized_data: dict[str, Any],
    rag_answer: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate a deterministic tool/API execution plan.
    
    This function analyzes the user request, normalized data, and RAG answer
    to decide whether tool/API execution would be recommended and whether
    human approval is required.
    
    Important: This does NOT execute anything. It generates a PLAN only.
    
    Args:
        user_request: The original user request text
        normalized_data: Normalized intake data (may include risk_level, etc.)
        rag_answer: Optional RAG-generated answer with context info
    
    Returns:
        Dict with:
        - requires_tool_or_api: bool - whether tool/API execution seems needed
        - execution_mode: str - always "planned_only" for Phase 3
        - allowed_to_execute: bool - always False for Phase 3
        - recommended_tools: list - tools that WOULD be used if approved
        - blocked_actions: list - actions that will never be allowed
        - approval_required: bool - whether human review is required
        - reason: str - explanation of the plan
    """
    
    # Extract risk level
    risk_level = normalized_data.get("risk_level", "medium")
    
    # Check if request implies system access
    needs_system_access = _detect_system_access_risk(user_request, normalized_data)
    
    # Check if RAG answer says context is insufficient
    rag_insufficient = _detect_rag_insufficient(rag_answer or {})
    
    # Determine if approval is required
    approval_required = (
        _infer_requires_approval(risk_level)
        or needs_system_access
        or rag_insufficient
    )
    
    # Determine if tool/API execution is needed
    requires_tool_or_api = needs_system_access or rag_insufficient
    
    # Recommended tools (deterministic mapping based on keywords)
    recommended_tools = []
    
    if requires_tool_or_api:
        request_lower = user_request.lower()
        
        # Check for legacy DB access
        if any(k in request_lower for k in ["legacy", "database", "db", "query"]):
            recommended_tools.append({
                "name": "legacy_db_lookup",
                "purpose": (
                    "Retrieve approved historical records through a controlled "
                    "backend interface"
                ),
                "requires_approval": True,
                "reason": (
                    "The request requires internal system data and should not be "
                    "executed directly by the LLM."
                ),
            })
        
        # Check for policy/configuration lookup
        if any(k in request_lower for k in ["policy", "configuration", "setting", "rule"]):
            recommended_tools.append({
                "name": "policy_lookup",
                "purpose": "Retrieve and apply internal policies or configuration",
                "requires_approval": True,
                "reason": (
                    "Policy decisions must be validated and approved before "
                    "application."
                ),
            })

        if any(k in request_lower for k in ["api", "endpoint", "service"]):
            recommended_tools.append({
                "name": "approved_api_gateway",
                "purpose": (
                    "Prepare a request through an approved internal API "
                    "gateway after human review"
                ),
                "requires_approval": True,
                "reason": (
                    "The request involves API access, so the LLM may only "
                    "produce a planned step."
                ),
            })

        if any(k in request_lower for k in ["tool", "integration", "connector"]):
            recommended_tools.append({
                "name": "approved_tool_catalog_lookup",
                "purpose": "Identify approved tools without invoking them",
                "requires_approval": True,
                "reason": (
                    "Tool-related requests must remain planned-only until "
                    "reviewed by a human."
                ),
            })
    
    # Actions that are always blocked
    blocked_actions = [
        "direct_sql_execution",
        "unapproved_external_api_call",
        "direct_database_write",
        "direct_system_command",
        "unapproved_file_operation",
    ]
    
    # Build reason text
    if not requires_tool_or_api:
        reason = (
            "No tool or API execution is needed. The RAG answer from the "
            "local knowledge base is sufficient to respond to this request."
        )
    elif approval_required:
        reason = (
            "The LLM must not directly access internal systems. This request "
            "involves sensitive operations (high risk level, internal data access, "
            "or insufficient context). Human review is required before execution."
        )
    else:
        reason = (
            "Tool or API execution may be beneficial, but human review is "
            "recommended for audit and compliance purposes."
        )
    
    return {
        "requires_tool_or_api": requires_tool_or_api,
        "execution_mode": "planned_only",
        "allowed_to_execute": False,
        "recommended_tools": recommended_tools,
        "blocked_actions": blocked_actions,
        "approval_required": approval_required,
        "reason": reason,
    }
