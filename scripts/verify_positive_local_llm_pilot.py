from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE_URL = os.getenv("OPERATOR_BASE_URL", "http://127.0.0.1:18701").rstrip("/")
MODEL = os.getenv("D3_LOCAL_LLM_MODEL", "qwen2.5:0.5b")
PROVIDER = os.getenv("D3_LOCAL_LLM_PROVIDER", "ollama-openai-compatible")
RUNTIME = os.getenv("D3_LOCAL_LLM_RUNTIME", "ollama-localhost")
ARTIFACT_DIR = Path(os.getenv("OPERATOR_ARTIFACT_DIR", "/tmp/operator-proof"))
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT = ARTIFACT_DIR / "d3_positive_local_llm_evidence.json"


def _json_request(path: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"} if data is not None else {},
        method="POST" if data is not None else "GET",
    )
    try:
        with urlopen(request, timeout=180) as response:
            body = json.loads(response.read().decode("utf-8"))
            if response.status != 200:
                raise AssertionError(f"{path} returned HTTP {response.status}: {body}")
            return body
    except HTTPError as exc:
        raise AssertionError(f"{path} returned HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')}") from exc


def _context_count(answer: dict) -> int:
    return sum(len(items or []) for items in (answer.get("retrieved_context") or {}).values())


def _source_labels(answer: dict) -> set[str]:
    labels: set[str] = set()
    for collection_name, items in (answer.get("retrieved_context") or {}).items():
        for item in items or []:
            metadata = item.get("metadata") or {}
            doc_id = str(metadata.get("doc_id") or "").strip()
            chunk_index = metadata.get("chunk_index", 0)
            if doc_id:
                labels.add(f"{collection_name}:{doc_id}:chunk-{chunk_index}")
    return labels


def main() -> None:
    _json_request("/api/rag/rebuild-index", {})

    question = (
        "How should an AI agent handle legacy database access and human approval? "
        "Cite at least one exact SOURCE label from the retrieved context in the answer."
    )
    positive = _json_request(
        "/api/rag/answer",
        {"question": question, "top_k_per_collection": 3, "model": MODEL},
    )

    model = positive.get("model") or {}
    answer_text = str(positive.get("answer") or "").strip()
    citations = positive.get("citations") or []
    retrieved_count = _context_count(positive)
    source_labels = _source_labels(positive)
    cited_labels = sorted(label for label in source_labels if label in answer_text)

    if model.get("available") is not True:
        raise AssertionError(f"Real local model was not positively available: {model}; error={positive.get('error')!r}")
    if str(model.get("name") or "") != MODEL:
        raise AssertionError(f"Expected exact model {MODEL!r}, got {model!r}")
    if not answer_text:
        raise AssertionError("Real local model returned empty generated output")
    if answer_text.startswith("Local LLM is unavailable"):
        raise AssertionError("Fallback text cannot satisfy positive local inference")
    if retrieved_count <= 0 or not citations:
        raise AssertionError("Positive inference must retain non-empty retrieved context and citations")
    if not source_labels or not cited_labels:
        raise AssertionError(
            "Generated answer must reference at least one exact SOURCE label from its retrieved context"
        )
    for citation in citations:
        if not str(citation.get("source_path") or "").strip():
            raise AssertionError(f"Citation is not source-verifiable: {citation!r}")

    missing_model = "guided-agent-d3-intentionally-missing-model"
    fallback = _json_request(
        "/api/rag/answer",
        {"question": question, "top_k_per_collection": 3, "model": missing_model},
    )
    fallback_model = fallback.get("model") or {}
    fallback_answer = str(fallback.get("answer") or "")
    if fallback_model.get("available") is not False:
        raise AssertionError(f"Unavailable-model fallback was not distinguishable: {fallback_model}")
    if not fallback_answer.startswith("Local LLM is unavailable"):
        raise AssertionError(f"Expected explicit fallback text, got {fallback_answer!r}")
    if _context_count(fallback) <= 0 or not (fallback.get("citations") or []):
        raise AssertionError("Fallback must preserve retrieved context/citations for inspection")

    evidence = {
        "destination": "D3 — Verified Local-LLM Controlled Operator Pilot",
        "milestone": "D3-01 / Issue #68",
        "positive_local_inference": True,
        "provider": PROVIDER,
        "model": MODEL,
        "runtime": RUNTIME,
        "base_url_boundary": "host-local OpenAI-compatible endpoint via Docker host gateway",
        "private_host_details_recorded": False,
        "question": question,
        "generated_answer_nonempty": True,
        "retrieved_context_count": retrieved_count,
        "citation_count": len(citations),
        "citation_sources": sorted({str(c.get("source_path") or "") for c in citations}),
        "generated_answer_source_labels": cited_labels,
        "fallback_separately_verified": True,
        "fallback_model": missing_model,
        "fallback_available": False,
        "controls_verified_elsewhere_in_same_exact_head_workflow": [
            "controlled approved run uses the same expected available local model",
            "explicit rejection causes no tool execution",
            "explicit approval gates allowlisted read-only legacy_db_lookup",
            "persisted correlated result/audit/retrieval provenance",
            "evidence export/reload/recovery visibility",
        ],
        "not_verified": [
            "customer production-system integration",
            "reviewer authentication or RBAC/SSO",
            "write/destructive tooling",
            "distributed exactly-once/recovery guarantees",
            "signing/non-repudiation/tamper-proof evidence",
            "unrestricted autonomy",
            "model-quality benchmark or SLA/SLO",
        ],
    }
    OUTPUT.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False))


if __name__ == "__main__":
    main()
