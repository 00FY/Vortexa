"""T-05: One action's approval cannot run another action, and wrong-hash approval leaves action HELD."""

from src.types import ActionRequest, Verdict, ErrorCode, Status
from src.erp_state import ERPState


def test_t05_approval_reuse_refused_leaves_action_held(gateway, dispute_task_id, collections_task_id, karan):
    state_before = gateway.erp.snapshot()

    # Action A: Legitimate payment of ₹15,000 by riya
    action_a = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 15000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec_a = gateway.evaluate(action_a, dispute_task_id)
    hash_a = dec_a.action_hash

    # Karan approves Action A
    gateway.approve(dec_a.action_id, approver=karan, action_hash=hash_a)

    # Action B: High-value collection action initiated by meera
    action_b = ActionRequest(
        agent_id="agent-003",
        action_type="initiate_collection",
        arguments={"amount": 80000.0, "account_id": "ACC-DEFAULT-44"},
        requested_by="meera",
    )
    dec_b = gateway.evaluate(action_b, collections_task_id)
    assert dec_b.verdict == Verdict.HOLD
    assert gateway.status(dec_b.action_id) == Status.HELD

    # Attacker tries to approve Action B using Action A's approval token/hash
    bad_attempt = gateway.approve(
        action_id=dec_b.action_id,
        approver=karan,
        action_hash=hash_a,  # WRONG hash!
    )

    # Verification 1: Refused with ERR_HASH_MISMATCH
    assert bad_attempt.error_code == ErrorCode.ERR_HASH_MISMATCH

    # Verification 2: Action B must REMAIN HELD (not killed or blocked by someone else's wrong guess)
    assert gateway.status(dec_b.action_id) == Status.HELD

    # Verification 3: Action B cannot execute in this state
    exec_b = gateway.execute(dec_b.action_id, action_b)
    assert not exec_b.success
    assert exec_b.error_code == ErrorCode.ERR_ACTION_NOT_PENDING

    # Verification 4: Legitimate approver can still approve Action B with its legitimate hash!
    legit_approval = gateway.approve(dec_b.action_id, approver=karan, action_hash=dec_b.action_hash)
    assert legit_approval.verdict == Verdict.ALLOW
    assert gateway.status(dec_b.action_id) == Status.APPROVED

    # Zero unauthorized mutations before legitimate execution
    state_after = gateway.erp.snapshot()
    assert state_after["collections_initiated"] == []
