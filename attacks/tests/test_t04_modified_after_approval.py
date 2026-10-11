"""T-04: An action edited after approval is refused and approval is invalidated permanently."""

import pytest
from src.types import ActionRequest, Verdict, ErrorCode, Status
from src.erp_state import ERPState


@pytest.mark.parametrize("edit_field,edit_value", [
    ("amount", 90000.0),
    ("bank_account", "ICICI-ATTACKER-999"),
    ("supplier_id", "SUP-ROGUE-77"),
    ("action_type", "update_supplier"),
])
def test_t04_modified_after_approval_refused_and_invalidated(gateway, dispute_task_id, karan, edit_field, edit_value):
    state_before = gateway.erp.snapshot()

    # Step 1: Legitimate payment of ₹15,000 requested by riya -> HELD
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 15000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )

    dec_eval = gateway.evaluate(action, dispute_task_id)
    assert dec_eval.verdict == Verdict.HOLD
    action_id = dec_eval.action_id
    original_hash = dec_eval.action_hash

    # Step 2: Karan approves the payment
    dec_appr = gateway.approve(action_id, approver=karan, action_hash=original_hash)
    assert dec_appr.verdict == Verdict.ALLOW
    assert gateway.status(action_id) == Status.APPROVED

    # Step 3: Attacker creates modified payload (either argument edit or action_type swap)
    if edit_field == "action_type":
        tampered_action = ActionRequest(
            agent_id=action.agent_id,
            action_type=edit_value,
            arguments=action.arguments,
            requested_by=action.requested_by,
            context_sources=action.context_sources,
        )
    else:
        tampered_action = action.with_arguments(**{edit_field: edit_value})

    # Step 4: Attempt execution with tampered payload
    res = gateway.execute(action_id, tampered_action)

    # Verification 1: Execution fails with ERR_HASH_MISMATCH
    assert not res.success
    assert res.error_code == ErrorCode.ERR_HASH_MISMATCH

    # Verification 2: Approval is dead! Status transitioned to INVALIDATED
    assert gateway.status(action_id) == Status.INVALIDATED

    # Verification 3: Re-attempting execution even with original payload now fails
    res_orig = gateway.execute(action_id, action)
    assert not res_orig.success
    assert res_orig.error_code == ErrorCode.ERR_HASH_MISMATCH

    # Verification 4: ERP untouched
    state_after = gateway.erp.snapshot()
    assert ERPState.diff(state_before, state_after) == {}
