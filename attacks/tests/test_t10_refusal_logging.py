"""T-10: Every refusal is logged."""

from src.types import ActionRequest, Verdict, AuditEvent, ErrorCode


def test_t10_every_refusal_is_logged(gateway, dispute_task_id, riya):
    action_1 = ActionRequest(
        agent_id="unauthorized_rogue_bot",
        action_type="process_payment",
        arguments={"amount": 1000.0},
        requested_by="anonymous",
    )
    gateway.evaluate(action_1, dispute_task_id)

    action_2 = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 40000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec_2 = gateway.evaluate(action_2, dispute_task_id)
    gateway.approve(dec_2.action_id, approver=riya, action_hash=dec_2.action_hash)

    logs = gateway.get_audit_log()
    refusal_events = [e for e in logs if e.event_name == AuditEvent.REFUSAL_LOGGED]

    assert len(refusal_events) >= 2
    error_codes = [e.details.get("error_code") for e in refusal_events]
    assert ErrorCode.ERR_UNKNOWN_AGENT.value in error_codes
    assert ErrorCode.ERR_SELF_APPROVAL.value in error_codes
