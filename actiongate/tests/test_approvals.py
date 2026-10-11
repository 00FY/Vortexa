import time
import pytest
from actiongate.approvals.manager import ApprovalManager
from actiongate.types import ErrorCode


def test_approval_registration_and_validation():
    mgr = ApprovalManager(ttl_seconds=300.0)
    fp = "hash-fp-101"
    mgr.register_approval("DEC-001", "MGR-002", "MANAGER", fp, "APPROVED")

    ok, sub, err, msg = mgr.validate_approval(fp, required_role="MANAGER")
    assert ok is True
    assert sub is not None
    assert sub.approver_id == "MGR-002"
    assert err is None


def test_approval_expired_after_ttl():
    mgr = ApprovalManager(ttl_seconds=1.0)
    fp = "hash-fp-expired"
    mgr.register_approval("DEC-002", "MGR-002", "MANAGER", fp, "APPROVED")

    # Fast forward past TTL
    mgr.registry[fp].timestamp = time.time() - 5.0

    ok, sub, err, msg = mgr.validate_approval(fp, required_role="MANAGER")
    assert ok is False
    assert err == ErrorCode.ERR_ACTION_NOT_PENDING
    assert "expired" in msg.lower()


def test_approval_replay_rejected():
    mgr = ApprovalManager(ttl_seconds=300.0)
    fp = "hash-fp-replay"
    mgr.register_approval("DEC-003", "MGR-002", "MANAGER", fp, "APPROVED")

    ok1, _, _, _ = mgr.validate_approval(fp)
    assert ok1 is True
    mgr.consume(fp)

    # Replay attempt
    ok2, _, err, msg = mgr.validate_approval(fp)
    assert ok2 is False
    assert err == ErrorCode.ERR_REPLAY
