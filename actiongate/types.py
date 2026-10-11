"""ActionGate Core Types and Request/Decision Contracts.

Grounds authorization decisions in three deterministic outcomes:
- ALLOW: Action satisfies explicit policies and permission boundaries; execution may proceed.
- HOLD: Action mandates human out-of-band verification (e.g. manager review).
- BLOCK: Action violates a security invariant, policy rule, or segregation of duties constraint.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import json
import hashlib
from pydantic import BaseModel, Field


class DecisionType(str, Enum):
    ALLOW = "ALLOW"
    HOLD = "HOLD"
    BLOCK = "BLOCK"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorCode(str, Enum):
    ERR_UNKNOWN_AGENT = "ERR_UNKNOWN_AGENT"
    ERR_UNKNOWN_ACTION = "ERR_UNKNOWN_ACTION"
    ERR_SELF_APPROVAL = "ERR_SELF_APPROVAL"
    ERR_HASH_MISMATCH = "ERR_HASH_MISMATCH"
    ERR_BLOCKED_BY_POLICY = "ERR_BLOCKED_BY_POLICY"
    ERR_ACTION_NOT_PENDING = "ERR_ACTION_NOT_PENDING"
    ERR_REPLAY = "ERR_REPLAY"
    ERR_UNAUTHORIZED_APPROVER = "ERR_UNAUTHORIZED_APPROVER"
    ERR_UNTRUSTED_ARGUMENT_ORIGIN = "ERR_UNTRUSTED_ARGUMENT_ORIGIN"
    ERR_TASK_SCOPE_VIOLATION = "ERR_TASK_SCOPE_VIOLATION"
    ERR_UNAUTHENTICATED = "ERR_UNAUTHENTICATED"


def calculate_action_fingerprint(
    action_type: str,
    target_resource: str,
    parameters: Dict[str, Any],
    requester_id: str,
) -> str:
    """
    Computes deterministic SHA-256 fingerprint over the canonical action proposal.
    Guarantees parameter immutability and approval binding.
    """
    normalized = {
        "action_type": action_type,
        "target_resource": target_resource,
        "parameters": parameters,
        "requester_id": requester_id,
    }
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class ActionGateRequest(BaseModel):
    request_id: str = Field(..., description="Unique idempotency trace ID for the action proposal")
    action_type: str = Field(..., description="Allowlisted enterprise action type name")
    target_resource: str = Field(..., description="Target entity or resource identifier")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Structured parameters for the action")
    requester_id: str = Field(..., description="Verified employee ID from authenticated ERP session")
    requester_role: str = Field(..., description="Verified role from authenticated ERP session")
    requester_department: str = Field("General", description="Verified department from authenticated ERP session")
    action_fingerprint: str = Field(..., description="Cryptographic SHA-256 fingerprint of the proposal")
    context_sources: List[Dict[str, Any]] = Field(default_factory=list, description="Provenance tracking context sources")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class HoldDetails(BaseModel):
    approval_workflow: str = "ERP_MANAGER_APPROVAL"
    required_role: str = "MANAGER"
    workflow_url: Optional[str] = "/erp/approvals"
    instructions: str = "This sensitive operation requires formal manager authorization in the ERP portal."


class ActionGateDecision(BaseModel):
    decision_id: str = Field(..., description="Unique decision audit record ID")
    request_id: str = Field(..., description="Matching request ID from the evaluation request")
    decision: DecisionType = Field(..., description="ALLOW, BLOCK, or HOLD decision")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Calculated WARS risk score between 0.0 and 1.0")
    risk_level: RiskLevel = Field(..., description="Categorized risk tier")
    reasons: List[str] = Field(default_factory=list, description="Policy evaluation explanations")
    action_fingerprint: str = Field(..., description="The exact fingerprint evaluated")
    approval_required_role: Optional[str] = None
    hold_details: Optional[HoldDetails] = None
    error_code: Optional[ErrorCode] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ActionGateApprovalSubmission(BaseModel):
    decision_id: str
    approver_id: str
    approver_role: str
    action_fingerprint: str
    status: str = "APPROVED"  # APPROVED or REJECTED
    notes: Optional[str] = None
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp())
