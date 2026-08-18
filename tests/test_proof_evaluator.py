from __future__ import annotations

import json

import pytest

from app.services import proof_evaluator


def test_fixed_dataset_has_expected_size_and_categories():
    cases = proof_evaluator.load_cases()
    assert len(cases) == 22
    assert {case["category"] for case in cases} == {
        "retrieval",
        "grounding",
        "routing",
        "tool_control",
    }


def test_load_cases_rejects_duplicate_ids(tmp_path):
    path = tmp_path / "cases.json"
    cases = [
        {"id": f"C{i:02d}", "category": "tool_control"}
        for i in range(20)
    ]
    cases[-1]["id"] = cases[0]["id"]
    path.write_text(json.dumps(cases), encoding="utf-8")
    with pytest.raises(ValueError, match="unique"):
        proof_evaluator.load_cases(path)


def test_run_evaluation_is_deterministic_with_fixed_boundaries(monkeypatch):
    cases = [
        {"id": "R", "category": "retrieval", "query": "q", "expected_source": "x.md", "max_rank": 3},
        {"id": "G", "category": "grounding", "query": "q", "expected_source": "x.md"},
        {"id": "C", "category": "routing", "user_request": "summary only", "risk_level": "low", "data_sources": ["agent_policy"], "expect_requires_tool": False, "expect_approval": False},
        {"id": "T", "category": "tool_control", "tool_name": "legacy_db_lookup", "approved": True, "allowed_tools": ["legacy_db_lookup"], "parameters": {"record_id": "LEG-001"}, "expect": "success", "expect_found": True},
    ]
    monkeypatch.setattr(
        proof_evaluator,
        "search_all_collections",
        lambda query, top_k_per_collection=3: [
            {"metadata": {"source_path": "x.md"}, "score": 1.0}
        ],
    )
    monkeypatch.setattr(
        proof_evaluator,
        "generate_rag_answer",
        lambda query, top_k_per_collection=3: {
            "citations": [{
                "doc_id": "d1",
                "title": "X",
                "source_path": "x.md",
                "collection": "agent_policy",
                "chunk_index": 0,
                "score": 1.0,
            }],
            "model": {"available": False},
            "error": None,
        },
    )

    first = proof_evaluator.run_evaluation(cases)
    second = proof_evaluator.run_evaluation(cases)
    assert first == second
    assert first["schema_version"] == 1
    assert first["total"] == 4
    assert first["passed"] == 4
    assert first["failed"] == 0
    assert first["all_passed"] is True


def test_tool_control_cases_cover_required_block_paths():
    cases = proof_evaluator.load_cases()
    results = {
        case["id"]: proof_evaluator.evaluate_case(case)
        for case in cases
        if case["category"] == "tool_control"
    }
    assert results["T01"]["passed"] is True
    assert results["T02"]["passed"] is True
    assert results["T03"]["checks"]["outcome"] == "blocked"
    assert results["T04"]["checks"]["outcome"] == "blocked"
    assert results["T05"]["checks"]["outcome"] == "blocked"
    assert results["T06"]["checks"]["outcome"] == "blocked"
    assert all(result["passed"] for result in results.values())


def test_routing_cases_preserve_planned_only_boundary():
    cases = proof_evaluator.load_cases()
    routing = [case for case in cases if case["category"] == "routing"]
    results = [proof_evaluator.evaluate_case(case) for case in routing]
    assert all(result["passed"] for result in results)
    for result in results:
        checks = result["checks"]
        assert checks["execution_mode"] == "planned_only"
        assert checks["allowed_to_execute"] is False
        assert "direct_sql_execution" in checks["blocked_actions"]
        assert "direct_database_write" in checks["blocked_actions"]
