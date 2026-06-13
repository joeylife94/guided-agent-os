"""
Validation service.

Checks intake data against the required fields defined in a template
and returns a list of missing field names.
"""

from __future__ import annotations


def find_missing_fields(
    intake_data: dict,
    required_fields: list[str],
) -> list[str]:
    """
    Return the names of required fields that are absent or empty in intake_data.

    A field is considered missing if:
    - it is not present in intake_data, or
    - its value is None, an empty string, or an empty list/dict.
    """
    missing: list[str] = []
    for field in required_fields:
        value = intake_data.get(field)
        if value is None:
            missing.append(field)
        elif isinstance(value, str) and not value.strip():
            missing.append(field)
        elif isinstance(value, (list, dict)) and not value:
            missing.append(field)
    return missing


def validate_intake(
    intake_data: dict,
    required_fields: list[str],
) -> tuple[bool, list[str]]:
    """
    Validate intake data against required fields.

    Returns:
        (is_valid, missing_fields) — is_valid is True when no required fields
        are missing.
    """
    missing = find_missing_fields(intake_data, required_fields)
    return len(missing) == 0, missing
