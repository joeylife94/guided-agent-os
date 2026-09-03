from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_controlled_operator_pilot_acceptance_assets_exist() -> None:
    workflow = ROOT / ".github" / "workflows" / "p025-controlled-operator-pilot.yml"
    verifier = ROOT / "scripts" / "verify_controlled_operator_pilot.py"
    runbook = ROOT / "docs" / "CONTROLLED_OPERATOR_PILOT.md"

    assert workflow.exists(), "P-025 requires one dedicated exact-head pilot acceptance workflow"
    assert verifier.exists(), "P-025 requires one coherent operator pilot verifier"
    assert runbook.exists(), "P-025 requires a reviewer-usable clean-environment runbook"


def test_controlled_operator_pilot_contract_is_destination_level() -> None:
    workflow = (ROOT / ".github" / "workflows" / "p025-controlled-operator-pilot.yml").read_text(encoding="utf-8")
    verifier = (ROOT / "scripts" / "verify_controlled_operator_pilot.py").read_text(encoding="utf-8")
    runbook = (ROOT / "docs" / "CONTROLLED_OPERATOR_PILOT.md").read_text(encoding="utf-8")
    combined = "\n".join([workflow, verifier, runbook])

    required_markers = [
        "structured_intake_and_grounding",
        "exact_execution_input_review",
        "rejection_blocks_execution",
        "approved_allowlisted_read_only_execution",
        "persisted_result_and_audit",
        "retrieval_provenance_verified",
        "evidence_export_reloaded",
        "recovery_visibility_verified",
        "controlled_operator_pilot_evidence.json",
    ]
    for marker in required_markers:
        assert marker in combined, f"P-025 pilot acceptance is missing required marker: {marker}"

    assert "docker compose -f compose.firebat.yml" in runbook
    assert "legacy_db_lookup" in combined
    assert "unrestricted autonomy" in runbook.lower()
    assert "customer production" in runbook.lower()
