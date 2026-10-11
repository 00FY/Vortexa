"""T-01: Unknown agent is blocked."""

from src.types import ActionRequest, Verdict, ErrorCode, AuditEvent
from src.erp_state import ERPState


def test_t01_unknown_agent_blocked(gateway, dispute_task_id):
    state_before = gateway.erp.snapshot()

    action = ActionRequest(
        agent_id="agent-999",
        action_type="process_payment",
        arguments={"amount": 5000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )

    decision = gateway.evaluate(action, dispute_task_id)

    assert decision.verdict == Verdict.BLOCK
    assert decision.rule_id == "RULE_AGENT_ALLOWLIST"
    assert decision.error_code == ErrorCode.ERR_UNKNOWN_AGENT

    exec_result = gateway.execute(decision.action_id, action)
    assert not exec_result.success
    assert exec_result.verdict == Verdict.BLOCK

    state_after = gateway.erp.snapshot()
    assert ERPState.diff(state_before, state_after) == {}

    audit_events = [e.event_name for e in gateway.get_audit_log()]
    assert AuditEvent.REFUSAL_LOGGED in audit_events
    assert AuditEvent.ACTION_BLOCKED in audit_events
