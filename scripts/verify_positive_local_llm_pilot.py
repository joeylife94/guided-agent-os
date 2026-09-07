from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = os.getenv("OPERATOR_BASE_URL", "http://127.0.0.1:18701").rstrip("/")
MODEL = os.getenv("D3_LOCAL_LLM_MODEL", "qwen2.5:1.5b")
PROVIDER = os.getenv("D3_LOCAL_LLM_PROVIDER", "ollama-openai-compatible")
RUNTIME = os.getenv("D3_LOCAL_LLM_RUNTIME", "ollama-localhost")
ARTIFACT_DIR = Path(os.getenv("OPERATOR_ARTIFACT_DIR", "/tmp/operator-proof"))
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT = ARTIFACT_DIR / "d3_positive_local_llm_evidence.json"
DIAGNOSTIC_OUTPUT = ARTIFACT_DIR / "d3_positive_local_llm_diagnostic.json"


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
        raise AssertionError(
            f"{path} returned HTTP {exc.code}: "
            f"{exc.read().decode('utf-8', errors='replace')}"
        ) from exc


def _query_all(question: str, top_k: int = 1) -> dict:
    query = urlencode({"q": question, "top_k": top_k})
    return _json_request(f"/api/rag/query-all?{query}")


def _context_count(answer: dict) -> int:
    return sum(
        len(items or [])
        for items in (answer.get("retrieved_context") or {}).values()
    )


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


def _select_required_source_label(discovery: dict) -> str:
    for collection_name, items in (discovery.get("results") or {}).items():
        for item in items or []:
            metadata = item.get("metadata") or {}
            doc_id = str(metadata.get("doc_id") or "").strip()
            if not doc_id:
                continue
            chunk_index = metadata.get("chunk_index", 0)
            return f"{collection_name}:{doc_id}:chunk-{chunk_index}"
    raise AssertionError("Preflight retrieval returned no usable SOURCE label")


def main() -> None:
    _json_request("/api/rag/rebuild-index", {})

    base_question = (
        "Using only the retrieved context, explain briefly how an AI agent should handle "
        "legacy database access and human approval."
    )

    # Discover one exact label from the same real semantic retrieval surface first.
    # This avoids hard-coding repository document IDs while still requiring the model
    # to emit a citation token that is demonstrably present in its returned context.
    discovery = _query_all(base_question, top_k=1)
    required_label = _select_required_source_label(discovery)

    question = (
        f"{base_question} Your final sentence MUST be exactly this citation token, copied "
        f"verbatim with no extra text after it: SOURCE [{required_label}]"
    )
    positive = _json_request(
        "/api/rag/answer",
        {"question": question, "top_k_per_collection": 1, "model": MODEL},
    )

    model = positive.get("model") or {}
    answer_text = str(positive.get("answer") or "").strip()
    citations = positive.get("citations") or []
    retrieved_count = _context_count(positive)
    source_labels = _source_labels(positive)
    cited_labels = sorted(label for label in source_labels if label in answer_text)

    diagnostic = {
        "provider": PROVIDER,
        "expected_model": MODEL,
        "runtime": RUNTIME,
        "model": model,
        "answer": answer_text,
        "retrieved_context_count": retrieved_count,
        "required_source_label": required_label,
        "required_source_present_in_returned_context": required_label in source_labels,
        "source_labels": sorted(source_labels),
        "cited_labels": cited_labels,
        "citations": citations,
        "error": positive.get("error"),
    }
    DIAGNOSTIC_OUTPUT.write_text(
        json.dumps(diagnostic, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({"d3_positive_diagnostic": diagnostic}, ensure_ascii=False))

    if model.get("available") is not True:
        raise AssertionError(
            f"Real local model was not positively available: {model}; "
            f"error={positive.get('error')!r}"
        )
    if str(model.get("name") or "") != MODEL:
        raise AssertionError(f"Expected exact model {MODEL!r}, got {model!r}")
    if not answer_text:
        raise AssertionError("Real local model returned empty generated output")
    if answer_text.startswith("Local LLM is unavailable"):
        raise AssertionError("Fallback text cannot satisfy positive local inference")
    if retrieved_count <= 0 or not citations:
        raise AssertionError(
            "Positive inference must retain non-empty retrieved context and citations"
        )
    if required_label not in source_labels:
        raise AssertionError(
            "The dynamically selected required SOURCE label must also be present in the "
            f"positive answer's returned context; required={required_label!r}; "
            f"source_labels={sorted(source_labels)!r}"
        )
    if required_label not in answer_text or not cited_labels:
        raise AssertionError(
            "Generated answer must contain the exact dynamically selected SOURCE label; "
            f"required={required_label!r}; answer={answer_text!r}"
        )
    for citation in citations:
        if not str(citation.get("source_path") or "").strip():
            raise AssertionError(f"Citation is not source-verifiable: {citation!r}")

    missing_model = "guided-agent-d3-intentionally-missing-model"
    fallback = _json_request(
        "/api/rag/answer",
        {"question": question, "top_k_per_collection": 1, "model": missing_model},
    )
    fallback_model = fallback.get("model") or {}
    fallback_answer = str(fallback.get("answer") or "")
    if fallback_model.get("available") is not False:
        raise AssertionError(
            f"Unavailable-model fallback was not distinguishable: {fallback_model}"
        )
    if not fallback_answer.startswith("Local LLM is unavailable"):
        raise AssertionError(f"Expected explicit fallback text, got {fallback_answer!r}")
    if _context_count(fallback) <= 0 or not (fallback.get("citations") or []):
        raise AssertionError(
            "Fallback must preserve retrieved context/citations for inspection"
        )

    evidence = {
        "destination": "D3 — Verified Local-LLM Controlled Operator Pilot",
        "milestone": "D3-01 / Issue #68",
        "positive_local_inference": True,
        "provider": PROVIDER,
        "model": MODEL,
        "runtime": RUNTIME,
        "base_url_boundary": (
            "host-local OpenAI-compatible endpoint via Docker host gateway"
        ),
        "private_host_details_recorded": False,
        "question": question,
        "generated_answer_nonempty": True,
        "retrieved_context_count": retrieved_count,
        "citation_count": len(citations),
        "citation_sources": sorted(
            {str(c.get("source_path") or "") for c in citations}
        ),
        "required_source_label": required_label,
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
    OUTPUT.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(evidence, ensure_ascii=False))


if __name__ == "__main__":
    main()
