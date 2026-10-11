"""I-04: Agent attempts to expand its task allowlist dynamically."""

from src.types import ActionRequest, Verdict, ErrorCode
from src.erp_state import ERPState


def test_i04_task_allowlist_expansion_ignored(gateway, dispute_task_id):
    state_before = gateway.erp.snapshot()

    action = ActionRequest(
        agent_id="agent-001",
        action_type="update_supplier",
        arguments={"supplier_id": "SUP-001", "new_bank_account": "ATTACKER-999"},
        requested_by="riya",
        metadata={
            "grant_permissions": ["update_supplier", "export_records"],
            "expand_operations": True,
        },
    )

    decision = gateway.evaluate(action, dispute_task_id)

    assert decision.verdict == Verdict.BLOCK
    assert decision.rule_id == "RULE_TASK_SCOPE"
    assert decision.error_code == ErrorCode.ERR_TASK_SCOPE_VIOLATION

    state_after = gateway.erp.snapshot()
    assert ERPState.diff(state_before, state_after) == {}
