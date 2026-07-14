import pytest

from job_application_agent.workflow_rules import (
    APPLICATION_PREP,
    ARCHIVE_JOB,
    DAILY_JOB_SCAN,
    WORKFLOW_RULE_CONTRACTS,
    build_workflow_rules_status,
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
    assert "mandatory baseline source groups" in lead_discovery["configurable_settings"]
    assert "stale-record criteria" in record_hygiene["configurable_settings"]
    assert "draft artifact types" in preparation["configurable_settings"]


def test_daily_scan_contract_exposes_coverage_completion_gate() -> None:
    status = build_workflow_rules_status(
        dry_run=True,
        require_human_approval=True,
        allow_external_submission=False,
    )
    policy = status["source_coverage_policy"]
    daily_scan = next(
        workflow
        for workflow in status["workflows"]
        if workflow["workflow_id"] == DAILY_JOB_SCAN
    )

    assert policy["baseline_required_each_run"] is True
    assert policy["baseline_direct_source_count"] == 20
    assert policy["conditional_additional_source_minimum"] == 20
    assert policy["conditional_expansion_excludes_baseline"] is True
    assert policy["zero_result_requires_complete_coverage"] is True
    assert policy["stable_identifiers_define_hard_duplicates"] is True
    assert daily_scan["alignment_checks"]["baseline_coverage_required"] is True
    assert daily_scan["alignment_checks"]["stable_identifier_deduplication"] is True


def test_unknown_workflow_contract_raises() -> None:
    with pytest.raises(ValueError, match="Unknown workflow rule contract"):
        get_workflow_rule_contract("unknown")
