"""
Normalization service for intake data.

Provides lightweight, deterministic normalization rules for intake data:
- Trims whitespace from string fields
- Extracts specific normalized fields
- Detects technology keywords and stack
- Preserves original intake_data for audit trail
"""

from __future__ import annotations

import re
from typing import Any


# ---------------------------------------------------------------------------
# Technology keyword detection
# ---------------------------------------------------------------------------

# Keywords to detect in project descriptions
TECH_KEYWORDS = {
    # Languages
    "python": ["python"],
    "javascript": ["javascript"],
    "typescript": ["typescript", "ts"],
    "java": ["java"],
    "csharp": ["c#", "csharp", ".net"],
    "go": ["golang"],
    "rust": ["rust"],
    # Frameworks
    "react": ["react", "reactjs"],
    "vue": ["vue", "vuejs"],
    "angular": ["angular"],
    "spring": ["spring"],
    "fastapi": ["fastapi"],
    "django": ["django"],
    "flask": ["flask"],
    "nextjs": ["next.js", "nextjs"],
    # Databases
    "postgresql": ["postgresql", "postgres", "psql"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "dynamodb": ["dynamodb"],
    # Cloud
    "aws": ["aws", "amazon"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],
    # Other
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "graphql": ["graphql"],
}


def _contains_keyword(text: str, keyword: str) -> bool:
    """Return True when keyword appears as a standalone token or phrase."""
    pattern = rf"(?<![A-Za-z0-9+#]){re.escape(keyword)}(?![A-Za-z0-9+#])"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def detect_keywords(text: str) -> list[str]:
    """
    Detect technology keywords in a text string.

    Returns a list of detected keywords (tech names) found in the text.
    Matching is case-insensitive.
    """
    if not text:
        return []

    detected: set[str] = set()

    for tech_name, keywords in TECH_KEYWORDS.items():
        for keyword in keywords:
            if _contains_keyword(text, keyword):
                detected.add(tech_name)
                break

    return sorted(list(detected))


def detect_stack(keywords: list[str]) -> list[str]:
    """
    Categorize detected keywords into a tech stack list.

    Returns a curated subset of keywords representing the primary tech stack.
    Organizes technologies by priority (languages, frameworks, DBs, etc.).
    """
    if not keywords:
        return []

    # Define priority order for display
    priority_order = [
        "python", "javascript", "typescript", "java", "csharp", "go", "rust",
        "react", "vue", "angular", "spring", "fastapi", "django", "flask", "nextjs",
        "postgresql", "mysql", "mongodb", "redis", "dynamodb",
        "aws", "azure", "gcp",
        "docker", "kubernetes", "graphql",
    ]

    # Keep keywords in priority order
    stack = [k for k in priority_order if k in keywords]
    return stack


def detect_language(keywords: list[str]) -> str | None:
    """
    Infer the primary programming language from detected keywords.

    Returns the first detected language, or None if no language keywords found.
    """
    language_keywords = {
        "python", "javascript", "typescript", "java", "csharp", "go", "rust"
    }
    for keyword in keywords:
        if keyword in language_keywords:
            return keyword
    return None


def detect_project_category(
    title: str,
    client_desc: str,
    project_desc: str,
) -> str:
    """
    Infer the project category from intake text.

    Returns a high-level category: 'web', 'mobile', 'backend', 'data',
    'devops', 'ml', 'other'.
    """
    combined_text = title + " " + client_desc + " " + project_desc

    # Check more specific categories first to avoid overlap
    # e.g., check backend before data (since "database" contains "data")
    category_keywords = {
        "devops": ["devops", "kubernetes", "docker", "ci/cd"],
        "ml": [
            "machine learning",
            "artificial intelligence",
            "ml",
            "nlp",
            "deep learning",
            "tensorflow",
        ],
        "mobile": ["mobile", "ios", "android", "native"],
        "backend": ["backend", "api", "rest", "graphql", "server"],
        "data": ["analytics", "etl", "pipeline", "warehouse"],
        "web": ["website", "frontend", "react", "vue", "angular", "ui", "ux"],
    }

    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if _contains_keyword(combined_text, keyword):
                return category

    return "other"


def _normalize_text(value: Any) -> str:
    """Return a stripped string for scalar intake values."""
    if value is None:
        return ""
    return str(value).strip()


def _normalize_string_list(value: Any) -> list[str]:
    """Normalize list-like intake fields into a list of non-empty strings."""
    if value is None:
        return []

    if isinstance(value, str):
        values = value.split(",")
    elif isinstance(value, (list, tuple, set)):
        values = value
    else:
        values = [value]

    normalized_values = []
    for item in values:
        text = _normalize_text(item)
        if text:
            normalized_values.append(text)
    return normalized_values


def _normalize_bool(value: Any) -> bool | None:
    """Normalize common yes/no intake values without guessing unknowns."""
    if isinstance(value, bool):
        return value
    if value is None:
        return None

    text = str(value).strip().lower()
    if text in {"yes", "true", "1", "required", "approval_required"}:
        return True
    if text in {"no", "false", "0", "not_required", "none"}:
        return False
    return None


# ---------------------------------------------------------------------------
# Normalization logic
# ---------------------------------------------------------------------------

def normalize_intake_data(intake_data: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize intake data into a cleaner internal structure.

    Takes raw intake_data and returns a normalized_data dict with:
    - normalized_title
    - normalized_client_description
    - normalized_project_description
    - detected_keywords (list of tech keywords found)
    - detected_stack (curated tech stack)
    - language (primary programming language or None)
    - project_category (inferred category)

    Rules:
    - Trims whitespace from string fields
    - Preserves None/missing fields
    - Detected keyword identifiers are lower-case canonical names
    - Original intake_data is NOT modified
    """
    normalized: dict[str, Any] = {}

    # Extract and normalize text fields
    title = (
        intake_data.get("opportunity_title", "").strip()
        if intake_data.get("opportunity_title")
        else ""
    )
    client_desc = (
        intake_data.get("client_description", "").strip()
        if intake_data.get("client_description")
        else ""
    )
    project_desc = (
        intake_data.get("project_description", "").strip()
        if intake_data.get("project_description")
        else ""
    )

    normalized["normalized_title"] = title
    normalized["normalized_client_description"] = client_desc
    normalized["normalized_project_description"] = project_desc

    # Detect keywords and stack
    full_text = f"{title} {client_desc} {project_desc}"
    keywords = detect_keywords(full_text)
    stack = detect_stack(keywords)
    language = detect_language(keywords)
    category = detect_project_category(title, client_desc, project_desc)

    normalized["detected_keywords"] = keywords
    normalized["detected_stack"] = stack
    normalized["language"] = language
    normalized["project_category"] = category

    # Generic controlled-agent fields. These are added alongside the
    # freelance-specific normalized fields so existing agents keep their
    # response shape while newer templates can share deterministic cleanup.
    text_fields = [
        "user_request",
        "business_context",
        "expected_output",
        "risk_level",
        "user_role",
        "security_constraints",
    ]
    for field in text_fields:
        if field in intake_data:
            normalized[field] = _normalize_text(intake_data.get(field))

    if "risk_level" in normalized:
        normalized["risk_level"] = normalized["risk_level"].lower()

    list_fields = ["data_sources", "allowed_tools"]
    for field in list_fields:
        if field in intake_data:
            normalized[field] = _normalize_string_list(intake_data.get(field))

    if "approval_required" in intake_data:
        normalized["approval_required"] = _normalize_bool(
            intake_data.get("approval_required")
        )

    return normalized
