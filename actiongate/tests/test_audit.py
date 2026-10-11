import pytest
from actiongate.audit.ledger import AuditLedger, AuditEvent
from actiongate.audit.verifier import AuditVerifier


def test_audit_hash_chain_valid():
    ledger = AuditLedger()
    ledger.log(AuditEvent.DECISION_RECORDED, "REQ-01", {"verdict": "ALLOW"})
    ledger.log(AuditEvent.EXECUTION_ATTEMPTED, "REQ-01", {"status": "SUCCESS"})
    ledger.log(AuditEvent.DECISION_RECORDED, "REQ-02", {"verdict": "HOLD"})

    is_valid, idx, msg = AuditVerifier.verify_chain(ledger.get_entries())
    assert is_valid is True
    assert idx is None
    assert "valid" in msg.lower()


def test_audit_tampering_detected():
    ledger = AuditLedger()
    ledger.log(AuditEvent.DECISION_RECORDED, "REQ-01", {"verdict": "ALLOW"})
    ledger.log(AuditEvent.DECISION_RECORDED, "REQ-02", {"verdict": "BLOCK"})
    ledger.log(AuditEvent.REFUSAL_LOGGED, "REQ-02", {"reason": "Policy violation"})

    entries = ledger.get_entries()
    # Attacker tampers with middle entry (changes BLOCK to ALLOW)
    entries[1].details["verdict"] = "ALLOW"

    is_valid, idx, msg = AuditVerifier.verify_chain(entries)
    assert is_valid is False
    assert idx == 1
    assert "modification detected" in msg.lower()
