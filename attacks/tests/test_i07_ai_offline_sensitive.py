"""I-07: AI model is offline and sensitive action requested."""

from src.types import ActionRequest, Verdict, DecisionPath
from src.erp_state import ERPState


def test_i07_ai_offline_sensitive_action_remains_held(gateway, kyc_task_id):
    state_before = gateway.erp.snapshot()

    gateway.ai_advisor.mode = "offline"

    action = ActionRequest(
        agent_id="agent-002",
        action_type="update_kyc",
        arguments={"customer_id": "CUST-002", "status": "verified"},
        requested_by="karan",
    )

    decision = gateway.evaluate(action, kyc_task_id)

    assert decision.verdict == Verdict.HOLD
    assert decision.rule_id == "RULE_MANDATORY_HOLD_KYC"
    assert decision.decision_path == DecisionPath.AI_UNAVAILABLE

    exec_result = gateway.execute(decision.action_id, action)
    assert not exec_result.success

    state_after = gateway.erp.snapshot()
    assert state_after["kyc_records"]["CUST-002"]["status"] == "pending"
    assert ERPState.diff(state_before, state_after) == {}
