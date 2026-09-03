# Controlled Operator Pilot — D2 Acceptance Runbook

This runbook demonstrates the existing bounded Guided Agent OS as a coherent **L4 Controlled Operator Pilot**. It composes accepted capabilities; it does not add autonomous authority.

## Boundaries

The pilot preserves human approval, policy checks, and the allowlisted read-only `legacy_db_lookup` fixture. It does **not** claim unrestricted autonomy, customer production integration, reviewer authentication/identity, RBAC/SSO, write or destructive tools, distributed recovery guarantees, signing/non-repudiation, or positive final-stack local-LLM inference.

## Clean-environment setup/start

```bash
cp .env.firebat.example .env.firebat
docker compose -f compose.firebat.yml down -v || true
docker compose -f compose.firebat.yml up --build -d
HEALTHCHECK_MAX_ATTEMPTS=90 sh scripts/healthcheck-firebat.sh
```

Open `http://127.0.0.1:8701/` for manual review, or execute the exact acceptance verifier below. CI uses port `18701` to avoid collisions.

## One coherent acceptance command

```bash
python -m pip install 'selenium==4.35.0'
OPERATOR_BASE_URL=http://127.0.0.1:8701 \
OPERATOR_ARTIFACT_DIR=/tmp/operator-proof \
python scripts/verify_controlled_operator_pilot.py
```

The verifier intentionally uses two independent operator runs: one rejected run to prove rejection blocks execution, and one approved run to prove the bounded read-only path. This avoids mutating or replaying a rejected decision into an approved one.

## Acceptance map

The machine-readable artifact `controlled_operator_pilot_evidence.json` records these destination-level assertions:

- `structured_intake_and_grounding` — structured intake reaches semantic RAG and renders the grounded review path.
- `exact_execution_input_review` — the Operator renders planned tool, exact parameters, allowlist, and reviewed execution-input digest from persisted state.
- `rejection_blocks_execution` — an explicit human rejection path completes without `TOOL_EXECUTED`.
- `approved_allowlisted_read_only_execution` — a separate approved run executes only `legacy_db_lookup` with the accepted fixture parameter contract.
- `persisted_result_and_audit` — result and ordered lifecycle audit are reloaded from persisted APIs and match the browser proof.
- `retrieval_provenance_verified` — persisted `RAG_RETRIEVED` evidence contains provider/model/dimension provenance.
- `evidence_export_reloaded` — deterministic run evidence is exported to JSON and reloaded with the same evidence digest.
- `recovery_visibility_verified` — the read-only `/api/agents/runs/recovery-queue` surface is reachable and returns a list, including an empty list when no interrupted decision exists.

The acceptance artifact is written to:

```text
/tmp/operator-proof/controlled_operator_pilot_evidence.json
```

The exported run evidence is written to:

```text
/tmp/operator-proof/controlled_operator_pilot_run_evidence.json
```

## Manual reviewer sequence

A reviewer can reproduce the same bounded product flow without private tribal knowledge:

1. Start from the clean Firebat compose environment and verify `/health`.
2. Submit incomplete structured intake and observe clarification rather than execution.
3. Complete the request and observe semantic grounding, citations, planned `legacy_db_lookup`, policy routing, exact tool parameters, allowlist, and execution-input digest.
4. Reject a pending run with a human rationale and confirm no read-only tool execution occurs.
5. Create a separate equivalent run, review the exact execution inputs, and explicitly approve it.
6. Confirm only the allowlisted read-only `legacy_db_lookup` fixture executes and the result is persisted.
7. Reload run events/evidence and inspect `RAG_RETRIEVED`, `APPROVED`, `TOOL_EXECUTED`, and `COMPLETED` correlation plus embedding provenance.
8. Export/reload the deterministic evidence JSON and confirm the same 64-character evidence digest.
9. Refresh the recovery queue and confirm bounded recovery/quarantine visibility. An empty queue is valid when no interrupted decision is present.

## Acceptance rule

D2 is accepted only when the exact PR head has successful PR Validation, Firebat baseline evidence where triggered, and the dedicated P-025 Controlled Operator Pilot workflow. Code presence or agent self-report alone is not PASS.
