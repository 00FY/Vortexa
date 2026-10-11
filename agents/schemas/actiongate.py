from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class DecisionType(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    HOLD = "HOLD"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ActionGateRequest(BaseModel):
    request_id: str = Field(..., description="Unique idempotency/trace ID for the action proposal")
    action_type: str = Field(..., description="Allowlisted action type name")
    target_resource: str = Field(..., description="Target entity or resource identifier")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Structured parameters for the action")
    requester_id: str = Field(..., description="Verified employee ID from authenticated ERP session")
    requester_role: str = Field(..., description="Verified role from authenticated ERP session")
    requester_department: str = Field(..., description="Verified department from authenticated ERP session")
    action_fingerprint: str = Field(..., description="Cryptographic SHA-256 fingerprint of the proposal")
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
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Calculated risk score between 0.0 and 1.0")
    risk_level: RiskLevel = Field(..., description="Categorized risk tier")
    reasons: List[str] = Field(default_factory=list, description="Policy evaluation explanations")
    action_fingerprint: str = Field(..., description="The exact fingerprint evaluated")
    approval_required_role: Optional[str] = None
    hold_details: Optional[HoldDetails] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ActionGateApprovalSubmission(BaseModel):
    decision_id: str
    approver_id: str
    approver_role: str
    action_fingerprint: str
    status: str = "APPROVED"  # APPROVED or REJECTED
    notes: Optional[str] = None
