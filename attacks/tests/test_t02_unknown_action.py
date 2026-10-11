"""T-02: Unknown action type is blocked."""

from src.types import ActionRequest, Verdict, ErrorCode, AuditEvent
from src.erp_state import ERPState


def test_t02_unknown_action_type_blocked(gateway, dispute_task_id):
    state_before = gateway.erp.snapshot()

    action = ActionRequest(
        agent_id="agent-001",
        action_type="delete_database_records",
        arguments={"table": "accounts", "condition": "all"},
        requested_by="riya",
    )

    decision = gateway.evaluate(action, dispute_task_id)

    assert decision.verdict == Verdict.BLOCK
    assert decision.rule_id == "RULE_ACTION_ALLOWLIST"
    assert decision.error_code == ErrorCode.ERR_UNKNOWN_ACTION

    exec_result = gateway.execute(decision.action_id, action)
    assert not exec_result.success

    state_after = gateway.erp.snapshot()
    assert ERPState.diff(state_before, state_after) == {}

    audit_events = [e.event_name for e in gateway.get_audit_log()]
    assert AuditEvent.REFUSAL_LOGGED in audit_events
    assert AuditEvent.ACTION_BLOCKED in audit_events
