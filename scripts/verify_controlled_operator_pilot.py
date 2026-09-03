from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen


BASE_URL = os.getenv("OPERATOR_BASE_URL", "http://127.0.0.1:18701").rstrip("/")
ARTIFACT_DIR = Path(os.getenv("OPERATOR_ARTIFACT_DIR", "/tmp/operator-proof"))
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT = ARTIFACT_DIR / "controlled_operator_pilot_evidence.json"
EXPORTED = ARTIFACT_DIR / "controlled_operator_pilot_run_evidence.json"


def _run(script: str) -> None:
    env = os.environ.copy()
    env["OPERATOR_BASE_URL"] = BASE_URL
    env["OPERATOR_ARTIFACT_DIR"] = str(ARTIFACT_DIR)
    subprocess.run([sys.executable, script], check=True, env=env)


def _get_json(path: str) -> object:
    with urlopen(f"{BASE_URL}{path}", timeout=20) as response:
        if response.status != 200:
            raise AssertionError(f"GET {path} returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    # Compose already-accepted browser proofs into one reviewer-runnable pilot.
    # The rejection proof uses a separate run and proves the human reject boundary
    # without creating TOOL_EXECUTED evidence; the golden path then proves approval
    # and allowlisted read-only execution.
    _run("scripts/verify_operator_rejection_rationale.py")
    _run("scripts/verify_operator_browser.py")

    browser_path = ARTIFACT_DIR / "operator-browser-evidence.json"
    rejection_path = ARTIFACT_DIR / "operator-rejection-rationale-evidence.json"
    browser = json.loads(browser_path.read_text(encoding="utf-8"))
    rejection = json.loads(rejection_path.read_text(encoding="utf-8"))

    if browser.get("failure"):
        raise AssertionError(f"Golden-path browser proof failed: {browser['failure']}")
    if rejection.get("failure"):
        raise AssertionError(f"Rejection browser proof failed: {rejection['failure']}")

    final_run_id = str(browser.get("final_run_id") or "").strip()
    if not final_run_id:
        raise AssertionError("Golden-path proof did not expose final_run_id")

    checks = set(browser.get("checks") or [])
    required_browser_checks = {
        "clarification_rendered",
        "approval_execution_inputs_match_persisted_run",
        "approved_execution_rendered",
        "persisted_execution_reloaded",
        "persisted_audit_reloaded_and_matches_ui",
        "reviewed_digest_matches_persisted_approval_execution_correlation",
    }
    missing = sorted(required_browser_checks - checks)
    if missing:
        raise AssertionError(f"Golden-path proof missing accepted checks: {missing}")

    # Persisted result/audit/provenance and deterministic evidence export/reload.
    evidence = _get_json(f"/api/agents/runs/{final_run_id}/evidence")
    if not isinstance(evidence, dict):
        raise AssertionError("Run evidence endpoint did not return an object")
    events = evidence.get("events") or []
    event_types = [event.get("event_type") for event in events]
    required_tail = ["RAG_RETRIEVED", "APPROVED", "TOOL_EXECUTED", "COMPLETED"]
    positions = [event_types.index(name) for name in required_tail]
    if positions != sorted(positions):
        raise AssertionError(f"Required lifecycle evidence is out of order: {event_types}")

    rag_event = next(event for event in events if event.get("event_type") == "RAG_RETRIEVED")
    rag_payload = rag_event.get("payload") or {}
    provenance = {
        "embedding_provider": rag_payload.get("embedding_provider"),
        "embedding_model": rag_payload.get("embedding_model"),
        "embedding_dimensions": rag_payload.get("embedding_dimensions"),
    }
    if not all(provenance.values()):
        raise AssertionError(f"Persisted retrieval provenance incomplete: {provenance}")

    persisted_run = evidence.get("run") or {}
    execution_result = (persisted_run.get("raw_output") or {}).get("execution_result") or {}
    if execution_result.get("status") != "executed" or execution_result.get("tool_name") != "legacy_db_lookup":
        raise AssertionError(f"Expected approved allowlisted read-only legacy_db_lookup execution: {execution_result}")

    digest = str(evidence.get("evidence_digest") or "")
    if len(digest) != 64:
        raise AssertionError(f"Expected 64-char deterministic evidence digest, got {digest!r}")

    EXPORTED.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    reloaded = json.loads(EXPORTED.read_text(encoding="utf-8"))
    if reloaded != evidence or reloaded.get("evidence_digest") != digest:
        raise AssertionError("Exported evidence did not reload byte-semantically to the same JSON object/digest")

    # Recovery visibility is deliberately read-only here. D2 requires an operator to
    # be able to see the bounded recovery queue, not to manufacture a crash in CI.
    recovery_queue = _get_json("/api/agents/runs/recovery-queue")
    if not isinstance(recovery_queue, list):
        raise AssertionError(f"Recovery queue is not a list: {recovery_queue!r}")

    result = {
        "destination": "D2 — L4 Controlled Operator Pilot",
        "base_url": BASE_URL,
        "approved_run_id": final_run_id,
        "structured_intake_and_grounding": True,
        "exact_execution_input_review": True,
        "rejection_blocks_execution": True,
        "approved_allowlisted_read_only_execution": True,
        "persisted_result_and_audit": True,
        "retrieval_provenance_verified": provenance,
        "evidence_export_reloaded": True,
        "evidence_digest": digest,
        "recovery_visibility_verified": True,
        "recovery_queue_size": len(recovery_queue),
        "source_artifacts": {
            "golden_path": str(browser_path),
            "rejection": str(rejection_path),
            "exported_run_evidence": str(EXPORTED),
        },
        "limitations": [
            "legacy_db_lookup is a deterministic local fixture, not customer production integration",
            "recovery visibility is read-only and does not claim distributed recovery guarantees",
            "no reviewer authentication, RBAC/SSO, write/destructive tools, unrestricted autonomy, signing/non-repudiation, or positive final-stack local-LLM claim",
        ],
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
