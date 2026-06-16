from app.api.routes import _get_template_config
from app.templates import public_enterprise_ai


def test_public_enterprise_ai_template_contract():
    assert public_enterprise_ai.AGENT_TYPE == "public_enterprise_ai"
    assert "use_case_title" in public_enterprise_ai.REQUIRED_FIELDS
    assert "business_domain" in public_enterprise_ai.REQUIRED_FIELDS
    assert "target_user_group" in public_enterprise_ai.REQUIRED_FIELDS
    assert "current_workflow_problem" in public_enterprise_ai.REQUIRED_FIELDS
    assert "data_sources" in public_enterprise_ai.REQUIRED_FIELDS
    assert "expected_agent_capabilities" in public_enterprise_ai.REQUIRED_FIELDS
    assert "legacy_systems" in public_enterprise_ai.OPTIONAL_FIELDS
    assert "security_constraints" in public_enterprise_ai.OPTIONAL_FIELDS
    assert "audit_requirements" in public_enterprise_ai.OPTIONAL_FIELDS


def test_public_enterprise_ai_template_is_registered():
    config = _get_template_config("public_enterprise_ai")

    assert config["required_fields"] == public_enterprise_ai.REQUIRED_FIELDS
    assert config["optional_fields"] == public_enterprise_ai.OPTIONAL_FIELDS
    assert config["clarification_map"] == public_enterprise_ai.CLARIFICATION_MAP
    assert "enterprise AI solution analyst" in config["analysis_prompt_template"]
    assert len(config["draft_action_templates"]) == 4
