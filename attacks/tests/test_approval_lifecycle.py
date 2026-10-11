"""Tests for human approval lifecycle edge cases: TTL expiry, fatigue isolation, and execution replays."""

import time
from src.types import ActionRequest, Verdict, Status, ErrorCode, AuditEvent
from src.erp_state import ERPState


def test_approval_expiry_ttl_enforced(gateway, dispute_task_id, karan):
    """
    Approval Expiry Guarantee:
    If an approved action is not executed within the allowed TTL window (e.g. 300 seconds),
    the gateway invalidates the approval, logs the event, and permanently refuses execution.
    """
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 25000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )

    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.HOLD

    # Approve properly
    app_dec = gateway.approve(dec.action_id, karan, dec.action_hash)
    assert app_dec.verdict == Verdict.ALLOW
    assert gateway.statuses[dec.action_id] == Status.APPROVED

    # Simulate TTL expiration by setting approval timestamp 301 seconds in the past
    gateway.approvals[dec.action_id].timestamp = time.time() - 301.0

    state_before = gateway.erp.snapshot()

    # Attempt execution after TTL
    res = gateway.execute(dec.action_id, action)

    assert not res.success
    assert res.verdict == Verdict.BLOCK
    assert res.error_code == ErrorCode.ERR_ACTION_NOT_PENDING
    assert "expired" in res.message.lower()

    # Approval should be invalidated
    assert gateway.statuses[dec.action_id] == Status.INVALIDATED
    assert dec.action_id not in gateway.approvals

    # ERP state must NOT have mutated
    state_after = gateway.erp.snapshot()
    assert ERPState.diff(state_before, state_after) == {}

    # Audit log contains approval.invalidated
    audit = gateway.get_audit_log()
    assert any(e.event_name == AuditEvent.APPROVAL_INVALIDATED and e.action_id == dec.action_id for e in audit)


def test_approval_fatigue_payload_isolation(gateway, dispute_task_id, karan):
    """
    Approval Fatigue & Payload Isolation:
    Rapid sequential approvals must evaluate cryptographic payload bindings independently.
    Approving Action A does not validate Action B, even under identical requestors and agents.
    """
    action_a = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 25000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    action_b = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 35000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )

    dec_a = gateway.evaluate(action_a, dispute_task_id)
    dec_b = gateway.evaluate(action_b, dispute_task_id)

    # Approver approves Action A
    app_a = gateway.approve(dec_a.action_id, karan, dec_a.action_hash)
    assert app_a.verdict == Verdict.ALLOW

    # Action B remains HELD until explicitly approved with its own hash
    assert gateway.statuses[dec_b.action_id] == Status.HELD

    # Executing Action B without approval fails
    res_b = gateway.execute(dec_b.action_id, action_b)
    assert not res_b.success
    assert res_b.error_code == ErrorCode.ERR_ACTION_NOT_PENDING


def test_simultaneous_double_execution_race_rejected(gateway, dispute_task_id, karan):
    """
    Execution Replay & Race Condition Prevention:
    When an approved action is executed once, any immediate re-execution call
    fails with ERR_REPLAY, and ERP state is debited exactly once.
    """
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 20000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )

    dec = gateway.evaluate(action, dispute_task_id)
    gateway.approve(dec.action_id, karan, dec.action_hash)

    # First execution succeeds
    res1 = gateway.execute(dec.action_id, action)
    assert res1.success

    # Immediate second execution is rejected
    res2 = gateway.execute(dec.action_id, action)
    assert not res2.success
    assert res2.error_code == ErrorCode.ERR_REPLAY

    # Verification: Payment debited only once (20000.0)
    matching_payments = [p for p in gateway.erp.payments_processed if p["action_id"] == dec.action_id]
    assert len(matching_payments) == 1
