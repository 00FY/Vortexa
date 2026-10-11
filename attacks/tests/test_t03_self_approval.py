"""T-03: Self-approval is refused."""

from src.types import ActionRequest, Verdict, ErrorCode, AuditEvent
from src.erp_state import ERPState


def test_t03_self_approval_refused(gateway, dispute_task_id, riya):
    state_before = gateway.erp.snapshot()

    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 45000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )

    decision = gateway.evaluate(action, dispute_task_id)
    assert decision.verdict == Verdict.HOLD

    approval_decision = gateway.approve(
        action_id=decision.action_id,
        approver=riya,  # Same user!
        action_hash=decision.action_hash,
    )

    assert approval_decision.verdict == Verdict.HOLD
    assert approval_decision.error_code == ErrorCode.ERR_SELF_APPROVAL
    assert approval_decision.rule_id == "RULE_NO_SELF_APPROVAL"

    exec_result = gateway.execute(decision.action_id, action)
    assert not exec_result.success

    state_after = gateway.erp.snapshot()
    assert ERPState.diff(state_before, state_after) == {}

    audit_events = [e.event_name for e in gateway.get_audit_log()]
    assert AuditEvent.REFUSAL_LOGGED in audit_events
