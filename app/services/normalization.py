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

    return normalized
