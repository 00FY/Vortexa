"""Deterministic Policy Engine enforcing ActionGate business invariants."""

from typing import Dict, Any, Tuple, Optional, Set
from actiongate.types import (
    ActionGateRequest,
    ActionGateDecision,
    DecisionType,
    RiskLevel,
    ErrorCode,
    HoldDetails,
)
from actiongate.risk.scorer import WeightedActionRiskScorer


# Supported Enterprise Operations
ALLOWLISTED_ACTIONS: Set[str] = {
    "hr.get_profile",
    "hr.get_directory",
    "leave.get_history",
    "leave.create",
    "expense.get_list",
    "expense.submit",
    "expense.approve",
    "process_payment",
    "update_supplier",
    "update_kyc",
    "export_records",
    "initiate_collection",
}


class PolicyEngine:
    def __init__(self):
        self.risk_scorer = WeightedActionRiskScorer()

    def evaluate(
        self,
        request: ActionGateRequest,
        approval_registry: Optional[Dict[str, Any]] = None,
    ) -> ActionGateDecision:
        """
        Evaluates proposal against strict deterministic policy invariants.
        AI advice or prompt content can NEVER relax these rules.
        """
        import uuid
        decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"
        reasons = []

        # Calculate WARS risk score
        risk_score, risk_level, _ = self.risk_scorer.compute_risk(request.model_dump())

        # Invariant 1: Action Allowlist
        if request.action_type not in ALLOWLISTED_ACTIONS:
            return ActionGateDecision(
                decision_id=decision_id,
                request_id=request.request_id,
                decision=DecisionType.BLOCK,
                risk_score=1.0,
                risk_level=RiskLevel.CRITICAL,
                reasons=[f"Action type '{request.action_type}' is unrecognized by gateway policy."],
                action_fingerprint=request.action_fingerprint,
                error_code=ErrorCode.ERR_UNKNOWN_ACTION,
            )

        # Invariant 2: Outbound Communication Block (Data Exfiltration Prevention)
        if request.action_type == "send_outbound" or "webhook" in request.target_resource.lower():
            return ActionGateDecision(
                decision_id=decision_id,
                request_id=request.request_id,
                decision=DecisionType.BLOCK,
                risk_score=1.0,
                risk_level=RiskLevel.CRITICAL,
                reasons=["Outbound transmission of enterprise data or messages is prohibited by policy."],
                action_fingerprint=request.action_fingerprint,
                error_code=ErrorCode.ERR_BLOCKED_BY_POLICY,
            )

        # Invariant 3: Sensitive Field Export Block
        if request.action_type == "export_records":
            fields = request.parameters.get("fields", [])
            sensitive_fields = {"salary", "ssn", "aadhaar", "pan", "password_hash", "pin"}
            if any(str(f).lower() in sensitive_fields for f in fields):
                return ActionGateDecision(
                    decision_id=decision_id,
                    request_id=request.request_id,
                    decision=DecisionType.BLOCK,
                    risk_score=1.0,
                    risk_level=RiskLevel.CRITICAL,
                    reasons=["Mass export of sensitive identity or compensation fields is prohibited by policy."],
                    action_fingerprint=request.action_fingerprint,
                    error_code=ErrorCode.ERR_BLOCKED_BY_POLICY,
                )

        # Invariant 4: Segregation of Duties (Self-Approval Strictly Prohibited)
        if request.action_type in ["expense.approve", "process_payment"]:
            target_claimant = request.parameters.get("employee_id") or request.parameters.get("claimant_id")
            if target_claimant and target_claimant == request.requester_id:
                return ActionGateDecision(
                    decision_id=decision_id,
                    request_id=request.request_id,
                    decision=DecisionType.BLOCK,
                    risk_score=1.0,
                    risk_level=RiskLevel.CRITICAL,
                    reasons=["Segregation of Duties Violation: Requester cannot approve their own financial claim."],
                    action_fingerprint=request.action_fingerprint,
                    error_code=ErrorCode.ERR_SELF_APPROVAL,
                )

        # Invariant 5: Read-only Operations
        if request.action_type in ["hr.get_profile", "hr.get_directory", "leave.get_history", "expense.get_list"]:
            return ActionGateDecision(
                decision_id=decision_id,
                request_id=request.request_id,
                decision=DecisionType.ALLOW,
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                reasons=["Read-only query permitted for authenticated user session."],
                action_fingerprint=request.action_fingerprint,
            )

        # Invariant 6: Routine Leave Creation
        if request.action_type == "leave.create":
            return ActionGateDecision(
                decision_id=decision_id,
                request_id=request.request_id,
                decision=DecisionType.ALLOW,
                risk_score=0.10,
                risk_level=RiskLevel.LOW,
                reasons=["Employee permitted to request leave for self; pending managerial calendar sync."],
                action_fingerprint=request.action_fingerprint,
            )

        # Invariant 7: Routine Expense Submission
        if request.action_type == "expense.submit":
            amount = float(request.parameters.get("amount", 0.0))
            return ActionGateDecision(
                decision_id=decision_id,
                request_id=request.request_id,
                decision=DecisionType.ALLOW,
                risk_score=risk_score,
                risk_level=risk_level,
                reasons=[f"Expense claim submission permitted (₹{amount:,.2f}); subject to manager review upon creation."],
                action_fingerprint=request.action_fingerprint,
            )

        # Invariant 8: Action Approval and Execution
        if request.action_type in ["expense.approve", "process_payment"]:
            target_id = request.parameters.get("expense_id") or request.target_resource
            amount = float(request.parameters.get("amount", 0.0))

            # Hard ceiling check
            if amount > 100000.0:
                return ActionGateDecision(
                    decision_id=decision_id,
                    request_id=request.request_id,
                    decision=DecisionType.BLOCK,
                    risk_score=1.0,
                    risk_level=RiskLevel.CRITICAL,
                    reasons=["Transaction amount exceeds maximum allowable gateway authorization ceiling (> ₹1,00,000)."],
                    action_fingerprint=request.action_fingerprint,
                    error_code=ErrorCode.ERR_BLOCKED_BY_POLICY,
                )

            # Check if out-of-band approval was already registered for exact fingerprint
            if approval_registry and request.action_fingerprint in approval_registry:
                submission = approval_registry[request.action_fingerprint]
                sub_status = getattr(submission, "status", None) or (submission.get("status") if isinstance(submission, dict) else None)
                if sub_status == "APPROVED":
                    approver = getattr(submission, "approver_id", None) or (submission.get("approver_id") if isinstance(submission, dict) else "AUTHORIZED_APPROVER")
                    return ActionGateDecision(
                        decision_id=decision_id,
                        request_id=request.request_id,
                        decision=DecisionType.ALLOW,
                        risk_score=0.20,
                        risk_level=RiskLevel.LOW,
                        reasons=[f"Verified exact-action approval from authorized manager {approver}."],
                        action_fingerprint=request.action_fingerprint,
                    )


            # Requires human out-of-band sign-off
            hold = HoldDetails(
                approval_workflow="ERP_MANAGER_APPROVAL",
                required_role="MANAGER",
                workflow_url=f"/erp/approvals/{target_id}",
                instructions="Sensitive operation mandates human supervisor authorization via ERP portal.",
            )
            return ActionGateDecision(
                decision_id=decision_id,
                request_id=request.request_id,
                decision=DecisionType.HOLD,
                risk_score=max(0.60, risk_score),
                risk_level=RiskLevel.HIGH,
                reasons=["High-value financial approval mandates out-of-band supervisor sign-off."],
                action_fingerprint=request.action_fingerprint,
                approval_required_role="MANAGER",
                hold_details=hold,
            )

        # Default fail-safe
        return ActionGateDecision(
            decision_id=decision_id,
            request_id=request.request_id,
            decision=DecisionType.HOLD,
            risk_score=risk_score,
            risk_level=risk_level,
            reasons=["Action requires human supervisor verification by default."],
            action_fingerprint=request.action_fingerprint,
        )
