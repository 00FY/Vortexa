"""T-06: When the AI is down, rules decide alone, and sensitive/risky actions remain held."""

import pytest
from src.types import ActionRequest, Verdict, DecisionPath


@pytest.mark.parametrize("amount,expected_verdict,expected_rule", [
    (5000.0, Verdict.ALLOW, "RULE_THRESHOLD_PAYMENT_AUTO"),
    (15000.0, Verdict.HOLD, "RULE_THRESHOLD_PAYMENT_HOLD"),
])
def test_t06_ai_unavailable_rules_decide(gateway, dispute_task_id, amount, expected_verdict, expected_rule):
    gateway.ai_advisor.mode = "offline"

    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": amount, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == expected_verdict
    assert dec.rule_id == expected_rule
    assert dec.decision_path == DecisionPath.AI_UNAVAILABLE

    # Assert decision_path is also preserved in audit log entry
    audit_entries = [e for e in gateway.get_audit_log() if e.action_id == dec.action_id]
    assert len(audit_entries) > 0
    assert any(e.details.get("decision_path") == "ai_unavailable" for e in audit_entries)

