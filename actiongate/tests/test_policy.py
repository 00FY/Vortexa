import pytest
from actiongate.types import (
    ActionGateRequest,
    DecisionType,
    RiskLevel,
    ErrorCode,
    calculate_action_fingerprint,
)
from actiongate.policy.engine import PolicyEngine


@pytest.fixture
def policy():
    return PolicyEngine()


def test_routine_query_allowed(policy):
    req = ActionGateRequest(
        request_id="REQ-001",
        action_type="hr.get_profile",
        target_resource="employee:EMP-001",
        parameters={"employee_id": "EMP-001"},
        requester_id="EMP-001",
        requester_role="EMPLOYEE",
        action_fingerprint="abc-123",
    )
    dec = policy.evaluate(req)
    assert dec.decision == DecisionType.ALLOW
    assert dec.risk_score == 0.0
    assert dec.risk_level == RiskLevel.LOW


def test_self_approval_blocked_by_policy(policy):
    # Requester attempting to approve their own expense
    fp = calculate_action_fingerprint("expense.approve", "expense:EXP-101", {"expense_id": "EXP-101", "claimant_id": "EMP-001"}, "EMP-001")
    req = ActionGateRequest(
        request_id="REQ-002",
        action_type="expense.approve",
        target_resource="expense:EXP-101",
        parameters={"expense_id": "EXP-101", "claimant_id": "EMP-001"},
        requester_id="EMP-001",
        requester_role="EMPLOYEE",
        action_fingerprint=fp,
    )
    dec = policy.evaluate(req)
    assert dec.decision == DecisionType.BLOCK
    assert dec.error_code == ErrorCode.ERR_SELF_APPROVAL
    assert dec.risk_score == 1.0


def test_unregistered_action_blocked(policy):
    req = ActionGateRequest(
        request_id="REQ-003",
        action_type="drop_database",
        target_resource="db:all",
        requester_id="EMP-001",
        requester_role="EMPLOYEE",
        action_fingerprint="fp-rogue",
    )
    dec = policy.evaluate(req)
    assert dec.decision == DecisionType.BLOCK
    assert dec.error_code == ErrorCode.ERR_UNKNOWN_ACTION


def test_high_value_expense_held_for_manager_approval(policy):
    req = ActionGateRequest(
        request_id="REQ-004",
        action_type="expense.approve",
        target_resource="expense:EXP-101",
        parameters={"expense_id": "EXP-101", "amount": 45000.0, "claimant_id": "EMP-002"},
        requester_id="MGR-002",
        requester_role="MANAGER",
        action_fingerprint="fp-held",
    )
    dec = policy.evaluate(req)
    assert dec.decision == DecisionType.HOLD
    assert dec.hold_details is not None
    assert dec.hold_details.required_role == "MANAGER"
