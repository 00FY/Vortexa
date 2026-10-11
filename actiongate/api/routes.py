"""ActionGate FastAPI REST API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List

from actiongate.types import (
    ActionGateRequest,
    ActionGateDecision,
    ActionGateApprovalSubmission,
)
from actiongate.policy.engine import PolicyEngine
from actiongate.approvals.manager import ApprovalManager
from actiongate.audit.ledger import AuditLedger, AuditEvent
from actiongate.audit.verifier import AuditVerifier

router = APIRouter()

# In-memory service state singletons
policy_engine = PolicyEngine()
approval_manager = ApprovalManager()
audit_ledger = AuditLedger()


@router.post("/api/v1/evaluate", response_model=ActionGateDecision)
def evaluate_action_proposal(request: ActionGateRequest) -> ActionGateDecision:
    """
    Evaluates proposed action against deterministic security policies and registered approvals.
    Logs evaluation decision into tamper-evident hash-chained audit ledger.
    """
    decision = policy_engine.evaluate(
        request=request,
        approval_registry=approval_manager.registry,
    )

    # Record decision in tamper-evident audit ledger
    audit_ledger.log(
        event_name=AuditEvent.DECISION_RECORDED,
        request_id=request.request_id,
        details={
            "action_type": request.action_type,
            "decision": decision.decision.value,
            "risk_score": decision.risk_score,
            "risk_level": decision.risk_level.value,
            "action_fingerprint": decision.action_fingerprint,
            "reasons": decision.reasons,
        },
    )

    return decision


@router.post("/api/v1/approvals")
def register_human_approval(submission: ActionGateApprovalSubmission) -> Dict[str, Any]:
    """
    Registers out-of-band human manager approval cryptographically bound to the exact action proposal fingerprint.
    """
    record = approval_manager.register_approval(
        decision_id=submission.decision_id,
        approver_id=submission.approver_id,
        approver_role=submission.approver_role,
        action_fingerprint=submission.action_fingerprint,
        status=submission.status,
        notes=submission.notes,
    )

    audit_ledger.log(
        event_name=AuditEvent.APPROVAL_REGISTERED,
        request_id=submission.decision_id,
        details={
            "approver_id": submission.approver_id,
            "approver_role": submission.approver_role,
            "action_fingerprint": submission.action_fingerprint,
            "status": submission.status,
        },
    )

    return {
        "status": "SUCCESS",
        "message": f"Approval recorded for fingerprint {submission.action_fingerprint[:12]}...",
        "record": record.model_dump(),
    }


@router.get("/api/v1/audit")
def get_audit_trail() -> Dict[str, Any]:
    """Returns audit entries along with cryptographic hash chain integrity verification."""
    entries = audit_ledger.get_entries()
    is_valid, failing_idx, verification_msg = AuditVerifier.verify_chain(entries)

    return {
        "total_entries": len(entries),
        "chain_valid": is_valid,
        "failing_index": failing_idx,
        "verification_message": verification_msg,
        "entries": [e.model_dump() for e in entries],
    }


@router.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "HEALTHY", "service": "ActionGate Authorization Engine"}
