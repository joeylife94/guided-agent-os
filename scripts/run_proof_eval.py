#!/usr/bin/env python3
"""Run the fixed Guided Agent OS Proof v1.0 evaluation suite."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.services.proof_evaluator import load_cases, run_evaluation
from app.services.rag_indexer import rebuild_rag_index


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(REPO_ROOT / "evaluation/cases.json"))
    parser.add_argument("--output", default=str(REPO_ROOT / "artifacts/proof-eval-results.json"))
    parser.add_argument(
        "--skip-index-rebuild",
        action="store_true",
        help="Use the existing compatible RAG index instead of rebuilding it.",
    )
    args = parser.parse_args()

    if not args.skip_index_rebuild:
        rebuild_rag_index()

    result = run_evaluation(load_cases(args.cases))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {key: result[key] for key in ("suite", "total", "passed", "failed", "all_passed")},
            indent=2,
        )
    )
    print(f"result_json={output_path}")
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
