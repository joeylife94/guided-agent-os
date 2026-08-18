"""Controlled read-only tool execution for Proof v1.0.

The LLM never calls these tools directly. Execution is only reached from the
human approval boundary after the planned tool name, caller allowlist, and
parameters have been validated.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


class ToolExecutionError(ValueError):
    """Raised when a planned tool execution violates the execution contract."""


@dataclass(frozen=True)
class ToolSpec:
    name: str
    read_only: bool
    required_parameters: frozenset[str]
    handler: Callable[[dict[str, Any]], dict[str, Any]]


_LEGACY_RECORDS: dict[str, dict[str, Any]] = {
    "LEG-001": {
        "record_id": "LEG-001",
        "system": "legacy_facility_registry",
        "status": "active",
        "summary": "Cooling unit inspection record available for review.",
    },
    "LEG-002": {
        "record_id": "LEG-002",
        "system": "legacy_facility_registry",
        "status": "archived",
        "summary": "Historical maintenance record retained for audit lookup.",
    },
}


def _legacy_db_lookup(parameters: dict[str, Any]) -> dict[str, Any]:
    record_id = parameters["record_id"]
    record = _LEGACY_RECORDS.get(record_id)
    if record is None:
        return {
            "found": False,
            "record_id": record_id,
            "record": None,
        }
    return {
        "found": True,
        "record_id": record_id,
        "record": dict(record),
    }


_TOOL_REGISTRY: dict[str, ToolSpec] = {
    "legacy_db_lookup": ToolSpec(
        name="legacy_db_lookup",
        read_only=True,
        required_parameters=frozenset({"record_id"}),
        handler=_legacy_db_lookup,
    ),
}

_TOOL_ALLOWLIST = frozenset({"legacy_db_lookup"})


def registered_tool_names() -> tuple[str, ...]:
    """Return the deterministic registry surface for inspection/tests."""
    return tuple(sorted(_TOOL_REGISTRY))


def _normalize_allowed_tools(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        return {value.strip()} if value.strip() else set()
    if isinstance(value, list):
        return {str(item).strip() for item in value if str(item).strip()}
    raise ToolExecutionError("allowed_tools must be a string or list of tool names")


def _validate_parameters(spec: ToolSpec, parameters: Any) -> dict[str, Any]:
    if not isinstance(parameters, dict):
        raise ToolExecutionError("tool_parameters must be an object")

    keys = set(parameters)
    missing = spec.required_parameters - keys
    unexpected = keys - spec.required_parameters
    if missing:
        raise ToolExecutionError(
            "Missing required tool parameters: " + ", ".join(sorted(missing))
        )
    if unexpected:
        raise ToolExecutionError(
            "Unexpected tool parameters: " + ", ".join(sorted(unexpected))
        )

    record_id = parameters.get("record_id")
    if not isinstance(record_id, str) or not record_id.strip():
        raise ToolExecutionError("record_id must be a non-empty string")

    return {"record_id": record_id.strip()}


def execute_approved_tool(
    *,
    tool_name: str,
    parameters: Any,
    approved: bool,
    allowed_tools: Any,
) -> dict[str, Any]:
    """Execute one deterministic read-only tool after explicit human approval."""
    if not approved:
        raise ToolExecutionError("Human approval is required before tool execution")

    spec = _TOOL_REGISTRY.get(tool_name)
    if spec is None:
        raise ToolExecutionError(f"Tool '{tool_name}' is not registered")
    if tool_name not in _TOOL_ALLOWLIST or not spec.read_only:
        raise ToolExecutionError(f"Tool '{tool_name}' is not allowlisted read-only")

    caller_allowlist = _normalize_allowed_tools(allowed_tools)
    if tool_name not in caller_allowlist:
        raise ToolExecutionError(
            f"Tool '{tool_name}' was not explicitly allowed for this run"
        )

    validated_parameters = _validate_parameters(spec, parameters)
    result = spec.handler(validated_parameters)
    return {
        "status": "executed",
        "tool_name": tool_name,
        "read_only": True,
        "parameters": validated_parameters,
        "result": result,
    }
