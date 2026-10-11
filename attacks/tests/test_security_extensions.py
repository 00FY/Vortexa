"""Additional Security Attack Tests: Task spoofing, Agent Approving, and Forged Tokens."""

from src.types import (
    ActionRequest,
    Verdict,
    ErrorCode,
    Principal,
    PrincipalType,
)


def test_forged_task_id_rejected(gateway):
    """Attack 1: Caller submits an action with a non-existent or forged task_id."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 5000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )

    decision = gateway.evaluate(action, "FORGED-TASK-999")
    assert decision.verdict == Verdict.BLOCK
    assert decision.error_code == ErrorCode.ERR_TASK_NOT_FOUND


def test_agent_principal_calling_approve_refused(gateway, dispute_task_id, rogue_agent_principal):
    """Attack 2: An agent attempts to call approve directly."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 40000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)

    appr = gateway.approve(dec.action_id, approver=rogue_agent_principal, action_hash=dec.action_hash)
    assert appr.error_code == ErrorCode.ERR_NOT_APPROVER
    assert appr.verdict == Verdict.HOLD


def test_forged_approver_token_rejected(gateway, dispute_task_id):
    """Attack 3: Caller forges a human approver name with an invalid/forged authentication token."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 40000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)

    imposter = Principal("karan", PrincipalType.HUMAN_USER, "kyc_officer", token="FORGED_TOKEN_123")
    appr = gateway.approve(dec.action_id, approver=imposter, action_hash=dec.action_hash)
    assert appr.error_code == ErrorCode.ERR_UNAUTHENTICATED
    assert appr.verdict == Verdict.HOLD
