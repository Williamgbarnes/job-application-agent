import pytest

from job_application_agent.workflow_rules import (
    APPLICATION_PREP,
    ARCHIVE_JOB,
    DAILY_JOB_SCAN,
    WORKFLOW_RULE_CONTRACTS,
    get_workflow_rule_contract,
)


def test_workflow_rule_contracts_cover_expected_templates() -> None:
    workflow_ids = {contract.workflow_id for contract in WORKFLOW_RULE_CONTRACTS}

    assert workflow_ids == {DAILY_JOB_SCAN, ARCHIVE_JOB, APPLICATION_PREP}


def test_every_template_has_configuration_shape() -> None:
    for contract in WORKFLOW_RULE_CONTRACTS:
        payload = contract.to_public_dict()
        assert payload["configurable_settings"]
        assert payload["allowed_inputs"]
        assert payload["allowed_outputs"]
        assert payload["required_controls"]
        assert payload["approval_required_before"]
        assert payload["prohibited_actions"]
        assert payload["no_op_behavior"]


def test_templates_expose_configuration_points() -> None:
    lead_discovery = get_workflow_rule_contract(DAILY_JOB_SCAN).to_public_dict()
    record_hygiene = get_workflow_rule_contract(ARCHIVE_JOB).to_public_dict()
    preparation = get_workflow_rule_contract(APPLICATION_PREP).to_public_dict()

    assert lead_discovery["label"] == "Lead discovery workflow template"
    assert record_hygiene["label"] == "Record hygiene workflow template"
    assert preparation["label"] == "Preparation workflow template"
    assert "source allowlist and priority" in lead_discovery["configurable_settings"]
    assert "stale-record criteria" in record_hygiene["configurable_settings"]
    assert "draft artifact types" in preparation["configurable_settings"]


def test_unknown_workflow_contract_raises() -> None:
    with pytest.raises(ValueError, match="Unknown workflow rule contract"):
        get_workflow_rule_contract("unknown")
