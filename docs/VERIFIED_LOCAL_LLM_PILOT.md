# D3 — Verified Local-LLM Controlled Operator Pilot

This runbook is the bounded D3-01 acceptance path for Issue #68. It does not expand tool authority or production claims.

## Accepted prerequisite

D1 L3 Usable/Demonstrable and D2 L4 Controlled Operator Pilot remain frozen. D3-01 only closes the positive final-stack local-LLM gap.

## Real-model contract

The acceptance environment must run a real local OpenAI-compatible endpoint. The repository workflow uses host-local Ollama on Ubuntu 24.04 and pulls `qwen2.5:0.5b`. The Firebat app connects through Docker's host gateway at the OpenAI-compatible `/v1` endpoint. No API key, cloud model, HTTP stub, or mocked `LocalLLMClient` is accepted.

Public-safe provenance recorded by the verifier:

- provider: `ollama-openai-compatible`
- exact model: `qwen2.5:0.5b`
- runtime class: `github-hosted-ubuntu-24.04-host-local-ollama`
- endpoint boundary: host-local OpenAI-compatible endpoint via Docker host gateway

Private runner addresses, tokens, or secrets are not evidence and must not be persisted.

## Acceptance sequence

1. Start Ollama locally and verify its API is reachable.
2. Pull `qwen2.5:0.5b`; do not substitute fallback or a cloud endpoint if the pull/run fails.
3. Build/start the existing Firebat controlled-pilot image with `LOCAL_LLM_BASE_URL=http://host.docker.internal:11434/v1` and `LOCAL_LLM_MODEL=qwen2.5:0.5b`.
4. Run `scripts/verify_positive_local_llm_pilot.py`.
   - rebuild semantic RAG index;
   - issue one grounded question with non-empty retrieved context;
   - require `model.available == true`, exact model match, non-empty generated output, and source-verifiable citations;
   - issue the same grounded question with an intentionally missing model and require explicit fallback with `model.available == false` while preserving citations/context.
5. On the same exact repository head, run `scripts/verify_controlled_operator_pilot.py` to re-prove the accepted D2 control boundary: explicit rejection/no execution, explicit approval, allowlisted read-only `legacy_db_lookup`, persisted correlated audit/result/retrieval provenance, evidence export/reload, and bounded recovery visibility.
6. Persist exact-head SHA, Ollama model inventory, positive-inference evidence, D2 acceptance evidence, and diagnostics as the workflow artifact.

## PASS rule

D3-01 may be accepted only when the exact candidate head's `D3 Positive Local LLM Pilot` workflow is green and the evidence artifact proves a real model was invoked. A generated file, unit test, stub server, mocked response, or normal fallback is not positive local inference evidence.

If the GitHub-hosted runner cannot practically install/run Ollama or the real model within the resource envelope, leave D3-01 in HOLD and execute the same verifier against an explicitly identified local machine on the exact candidate head. Do not weaken the gate.

## Non-claims

This acceptance does not establish customer production integration, reviewer authentication/RBAC/SSO, write/destructive tool safety, unrestricted autonomy, distributed exactly-once/recovery guarantees, signing/non-repudiation/tamper-proof evidence, benchmark quality, cloud/Kubernetes production readiness, SLA/SLO, or security/compliance certification.
