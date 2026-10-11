"""T-09: A held, rejected, or blocked action cannot run."""

from src.types import ActionRequest, Verdict, ErrorCode
from src.erp_state import ERPState


def test_t09_held_or_blocked_action_cannot_run(gateway, dispute_task_id):
    state_before = gateway.erp.snapshot()

    # Case A: Action that is HELD
    held_action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 25000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec_held = gateway.evaluate(held_action, dispute_task_id)
    assert dec_held.verdict == Verdict.HOLD

    exec_held = gateway.execute(dec_held.action_id, held_action)
    assert not exec_held.success
    assert exec_held.error_code == ErrorCode.ERR_ACTION_NOT_PENDING

    # Case B: Action that is BLOCKED
    blocked_action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 150000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec_blocked = gateway.evaluate(blocked_action, dispute_task_id)
    assert dec_blocked.verdict == Verdict.BLOCK

    exec_blocked = gateway.execute(dec_blocked.action_id, blocked_action)
    assert not exec_blocked.success
    assert exec_blocked.error_code == ErrorCode.ERR_ACTION_NOT_PENDING

    state_after = gateway.erp.snapshot()
    assert ERPState.diff(state_before, state_after) == {}
