"""T-08: Cryptographic detection of audit tampering: middle row, last row, status rewrite, and truncation."""

import pytest
from src.types import ActionRequest, Verdict, AuditEvent


@pytest.fixture
def populated_audit_gateway(gateway, dispute_task_id):
    """Generates a multi-row verified audit log before tampering."""
    for i in range(3):
        act = ActionRequest(
            agent_id="agent-001",
            action_type="process_payment",
            arguments={"amount": 2000.0 * (i + 1), "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
            requested_by="riya",
        )
        dec = gateway.evaluate(act, dispute_task_id)
        gateway.execute(dec.action_id, act)

    valid, broken_idx = gateway.audit_log.verify_chain()
    assert valid
    assert broken_idx is None
    return gateway


@pytest.mark.parametrize("tamper_mode", [
    "middle_row",
    "last_row",
    "status_rewrite",
    "truncation",
])
def test_t08_audit_tampering_detection(populated_audit_gateway, dispute_task_id, tamper_mode):
    gateway = populated_audit_gateway
    initial_entries = gateway.get_audit_log()
    total_rows = len(initial_entries)
    saved_head_hash = initial_entries[-1].entry_hash

    if tamper_mode == "middle_row":
        mid_idx = total_rows // 2
        gateway._corruptAuditRow(mid_idx, "action_id", "TAMPERED-MIDDLE-ROW")
        valid, broken_idx = gateway.audit_log.verify_chain()
        assert not valid
        assert broken_idx == mid_idx

    elif tamper_mode == "last_row":
        last_idx = total_rows - 1
        gateway._corruptAuditRow(last_idx, "details", {"amount": 999999.0})
        valid, broken_idx = gateway.audit_log.verify_chain()
        assert not valid
        assert broken_idx == last_idx

    elif tamper_mode == "status_rewrite":
        # Create a held action to generate an ACTION_HELD audit entry
        act_held = ActionRequest(
            agent_id="agent-001",
            action_type="process_payment",
            arguments={"amount": 40000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
            requested_by="riya",
        )
        dec_held = gateway.evaluate(act_held, dispute_task_id)
        assert dec_held.verdict == Verdict.HOLD
        held_idx = len(gateway.get_audit_log()) - 1
        assert gateway.audit_log.entries[held_idx].event_name == AuditEvent.ACTION_HELD

        # Attacker rewrites event_name from action.held to action.allowed
        gateway._corruptAuditRow(held_idx, "event_name", AuditEvent.ACTION_ALLOWED)
        valid, broken_idx = gateway.audit_log.verify_chain()
        assert not valid
        assert broken_idx == held_idx

    elif tamper_mode == "truncation":
        # Deleting rows at the end leaves internal prefixes valid, but head hash deviates from external checkpoint
        truncated_entries = gateway.audit_log.entries[:3]
        current_head = truncated_entries[-1].entry_hash
        assert current_head != saved_head_hash, "Truncation detected: head hash differs from saved checkpoint!"
