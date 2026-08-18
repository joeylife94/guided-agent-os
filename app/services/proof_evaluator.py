"""Deterministic Proof v1.0 evaluation harness.

The evaluator reuses existing retrieval, answer-generation, planning and
controlled-execution boundaries. It does not duplicate workflow logic or add a
benchmarking platform. Results are plain JSON so CI and P6 documentation can
consume the same artifact.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from app.services.rag_answerer import generate_rag_answer
from app.services.rag_retriever import search_all_collections
from app.services.tool_executor import ToolExecutionError, execute_approved_tool
from app.services.tool_plan_generator import generate_tool_plan

DEFAULT_CASES_PATH = Path("evaluation/cases.json")


def load_cases(path: str | Path = DEFAULT_CASES_PATH) -> list[dict[str, Any]]:
    cases = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("evaluation cases must be a non-empty JSON array")
    ids = [case.get("id") for case in cases]
    if any(not isinstance(case_id, str) or not case_id for case_id in ids):
        raise ValueError("every evaluation case must have a non-empty string id")
    if len(ids) != len(set(ids)):
        raise ValueError("evaluation case ids must be unique")
    if not 20 <= len(cases) <= 30:
        raise ValueError("Proof v1.0 evaluation dataset must contain 20 to 30 cases")
    return cases


def _source_rank(results: Iterable[dict[str, Any]], expected_source: str) -> int | None:
    for rank, result in enumerate(results, start=1):
        if (result.get("metadata") or {}).get("source_path") == expected_source:
            return rank
    return None


def _evaluate_retrieval(case: dict[str, Any]) -> dict[str, Any]:
    results = search_all_collections(case["query"], top_k_per_collection=3)
    rank = _source_rank(results, case["expected_source"])
    max_rank = int(case.get("max_rank", 3))
    passed = rank is not None and rank <= max_rank
    return {
        "passed": passed,
        "checks": {
            "expected_source": case["expected_source"],
            "observed_rank": rank,
            "max_rank": max_rank,
        },
    }


def _evaluate_grounding(case: dict[str, Any]) -> dict[str, Any]:
    answer = generate_rag_answer(case["query"], top_k_per_collection=3)
    citations = answer.get("citations") or []
    expected_source = case["expected_source"]
    source_paths = [citation.get("source_path") for citation in citations]
    citation_fields_ok = all(
        all(key in citation for key in ("doc_id", "title", "source_path", "collection", "chunk_index", "score"))
        for citation in citations
    )
    expected_present = expected_source in source_paths
    passed = bool(citations) and citation_fields_ok and expected_present
    return {
        "passed": passed,
        "checks": {
            "citation_count": len(citations),
            "citation_fields_complete": citation_fields_ok,
            "expected_source": expected_source,
            "expected_source_cited": expected_present,
            "model_available": bool((answer.get("model") or {}).get("available")),
            "error": answer.get("error"),
        },
    }


def _evaluate_routing(case: dict[str, Any]) -> dict[str, Any]:
    normalized_data = {
        "risk_level": case["risk_level"],
        "data_sources": case.get("data_sources", []),
    }
    plan = generate_tool_plan(
        user_request=case["user_request"],
        normalized_data=normalized_data,
        rag_answer={"answer": "Relevant context is available."},
    )
    checks: dict[str, Any] = {
        "requires_tool_or_api": plan["requires_tool_or_api"],
        "approval_required": plan["approval_required"],
        "execution_mode": plan["execution_mode"],
        "allowed_to_execute": plan["allowed_to_execute"],
        "blocked_actions": plan["blocked_actions"],
    }
    passed = (
        plan["requires_tool_or_api"] is case["expect_requires_tool"]
        and plan["approval_required"] is case["expect_approval"]
        and plan["execution_mode"] == "planned_only"
        and plan["allowed_to_execute"] is False
        and "direct_sql_execution" in plan["blocked_actions"]
        and "direct_database_write" in plan["blocked_actions"]
    )
    expected_tool = case.get("expect_tool")
    if expected_tool:
        observed_tools = [item.get("name") for item in plan.get("recommended_tools", [])]
        checks["expected_tool"] = expected_tool
        checks["observed_tools"] = observed_tools
        passed = passed and expected_tool in observed_tools
    return {"passed": passed, "checks": checks}


def _evaluate_tool_control(case: dict[str, Any]) -> dict[str, Any]:
    try:
        result = execute_approved_tool(
            tool_name=case["tool_name"],
            parameters=case["parameters"],
            approved=case["approved"],
            allowed_tools=case["allowed_tools"],
        )
    except ToolExecutionError as exc:
        return {
            "passed": case["expect"] == "blocked",
            "checks": {"outcome": "blocked", "error": str(exc)},
        }

    passed = case["expect"] == "success" and result.get("status") == "executed"
    if "expect_found" in case:
        observed_found = bool((result.get("result") or {}).get("found"))
        passed = passed and observed_found is case["expect_found"]
    else:
        observed_found = None
    return {
        "passed": passed,
        "checks": {
            "outcome": "success",
            "status": result.get("status"),
            "tool_name": result.get("tool_name"),
            "read_only": result.get("read_only"),
            "found": observed_found,
        },
    }


_EVALUATORS = {
    "retrieval": _evaluate_retrieval,
    "grounding": _evaluate_grounding,
    "routing": _evaluate_routing,
    "tool_control": _evaluate_tool_control,
}


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    category = case.get("category")
    evaluator = _EVALUATORS.get(category)
    if evaluator is None:
        raise ValueError(f"unsupported evaluation category: {category!r}")
    result = evaluator(case)
    return {
        "id": case["id"],
        "category": category,
        "passed": bool(result["passed"]),
        "checks": result["checks"],
    }


def run_evaluation(cases: list[dict[str, Any]]) -> dict[str, Any]:
    results = [evaluate_case(case) for case in cases]
    category_summary: dict[str, dict[str, int]] = {}
    for result in results:
        summary = category_summary.setdefault(result["category"], {"passed": 0, "total": 0})
        summary["total"] += 1
        summary["passed"] += int(result["passed"])
    passed = sum(int(result["passed"]) for result in results)
    return {
        "schema_version": 1,
        "suite": "guided-agent-os-proof-v1",
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "all_passed": passed == len(results),
        "categories": category_summary,
        "results": results,
    }
