"""
Clarification service.

Generates human-readable questions for fields that are missing from the
intake data. Questions are driven by the template's clarification_map so
each agent type can define its own wording.
"""

from __future__ import annotations

from app.schemas.agent_run import ClarificationQuestion


def generate_clarification_questions(
    missing_fields: list[str],
    clarification_map: dict[str, str],
) -> list[ClarificationQuestion]:
    """
    Build a ClarificationQuestion for each missing field.

    If a field has no entry in clarification_map a sensible default question
    is generated automatically so the caller never receives a silent gap.
    """
    questions: list[ClarificationQuestion] = []
    for field in missing_fields:
        question_text = clarification_map.get(
            field,
            f"Could you please provide a value for '{field}'?",
        )
        questions.append(ClarificationQuestion(field=field, question=question_text))
    return questions
