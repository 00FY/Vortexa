"""T-07: A garbage or 'allow everything' AI answer relaxes nothing."""

from src.types import ActionRequest, Verdict, DecisionPath


def test_t07_unsafe_ai_cannot_relax_rules(gateway, dispute_task_id):
    gateway.ai_advisor.mode = "adversarial_allow_all"

    # Action: ₹50,000 payment which deterministic rules strictly place on HOLD
    action_hold = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 50000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )

    decision_hold = gateway.evaluate(action_hold, dispute_task_id)
    assert decision_hold.ai_recommendation == Verdict.ALLOW
    assert decision_hold.verdict == Verdict.HOLD
    assert decision_hold.rule_id == "RULE_THRESHOLD_PAYMENT_HOLD"
    # Decision path was rules_only because AI's allow attempt was ignored
    assert decision_hold.decision_path == DecisionPath.RULES_ONLY

    # Action 2: Action > ₹100,000 which rules strictly BLOCK
    action_block = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 250000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    decision_block = gateway.evaluate(action_block, dispute_task_id)
    assert decision_block.ai_recommendation == Verdict.ALLOW
    assert decision_block.verdict == Verdict.BLOCK
    assert decision_block.rule_id == "RULE_THRESHOLD_PAYMENT_BLOCK"
    assert decision_block.decision_path == DecisionPath.RULES_ONLY
