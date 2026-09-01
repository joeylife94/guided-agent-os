from __future__ import annotations

import hashlib
import json


def reviewed_digest(
    *,
    tool_name: str = "legacy_db_lookup",
    tool_parameters: dict | None = None,
    allowed_tools: list[str] | None = None,
) -> str:
    snapshot = {
        "tool_name": tool_name,
        "tool_parameters": {"record_id": "LEG-001"} if tool_parameters is None else tool_parameters,
        "allowed_tools": ["legacy_db_lookup"] if allowed_tools is None else allowed_tools,
    }
    canonical = json.dumps(
        snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def approval_body(note: str = "Approved after reviewing exact execution inputs", **kwargs) -> dict:
    return {
        "note": note,
        "expected_execution_inputs_digest": reviewed_digest(**kwargs),
    }
