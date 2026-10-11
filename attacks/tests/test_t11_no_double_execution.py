"""T-11: An action cannot run twice (Replay Protection)."""

from src.types import ActionRequest, Verdict, ErrorCode, AuditEvent
from src.erp_state import ERPState


def test_t11_no_double_execution(gateway, dispute_task_id):
    state_before = gateway.erp.snapshot()
    initial_balance = gateway.erp.accounts["ops_account"]

    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 4000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )

    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.ALLOW

    exec_1 = gateway.execute(dec.action_id, action)
    assert exec_1.success
    assert gateway.erp.accounts["ops_account"] == initial_balance - 4000.0

    exec_2 = gateway.execute(dec.action_id, action)
    assert not exec_2.success
    assert exec_2.error_code == ErrorCode.ERR_REPLAY

    assert gateway.erp.accounts["ops_account"] == initial_balance - 4000.0
    assert len(gateway.erp.payments_processed) == 1

    audit_events = [e.event_name for e in gateway.get_audit_log()]
    assert AuditEvent.REFUSAL_LOGGED in audit_events
