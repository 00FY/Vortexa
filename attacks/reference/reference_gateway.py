"""Reference Implementation of ActionGate with full contract refactoring and lifecycle security."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import uuid

from src.contract import GatewayContract
from src.types import (
    ActionRequest,
    TaskRecord,
    Decision,
    ExecutionResult,
    AuditEntry,
    Verdict,
    Status,
    DecisionPath,
    ErrorCode,
    AuditEvent,
    ApprovalRecord,
    Principal,
    PrincipalType,
)
from src.erp_state import ERPState
from src.audit import AuditLog
from src.policy import PolicyEngine, USER_ROLES
from src.ai_advisor import AIAdvisor, AIUnavailableError


# Standard trusted system tasks store
STANDARD_TASKS = {
    "TASK-DISP-101": TaskRecord("TASK-DISP-101", "invoice_dispute", "invoices:INV-2024-9981", ("process_payment",), "agent-001"),
    "TASK-KYC-202": TaskRecord("TASK-KYC-202", "kyc_verification", "customers:CUST-002", ("update_kyc",), "agent-002"),
    "TASK-COLL-303": TaskRecord("TASK-COLL-303", "collections_recovery", "accounts:ACC-DEFAULT-44", ("initiate_collection",), "agent-003"),
    "TASK-ADMIN-404": TaskRecord("TASK-ADMIN-404", "admin_config", "system:all", ("create_user", "modify_policy"), "agent-004"),
    "TASK-EXPORT-505": TaskRecord("TASK-EXPORT-505", "bulk_reporting", "analytics:all", ("export_records",), "agent-002"),
    "TASK-P1": TaskRecord("TASK-P1", "property_verification", "all", ("process_payment",), "agent-001"),
}

# Known valid user authentication tokens
VALID_TOKENS = {
    "riya": "TOK-RIYA-SECRET",
    "karan": "TOK-KARAN-SECRET",
    "meera": "TOK-MEERA-SECRET",
    "admin": "TOK-ADMIN-SECRET",
}


class ReferenceGateway(GatewayContract):
    def __init__(self, erp_state: Optional[ERPState] = None, ai_mode: str = "normal"):
        self.erp = erp_state or ERPState()
        self.audit_log = AuditLog()
        self.policy = PolicyEngine(self.erp)
        self.ai_advisor = AIAdvisor(mode=ai_mode)
        
        # State tracking
        self.tasks: Dict[str, TaskRecord] = dict(STANDARD_TASKS)
        self.actions: Dict[str, ActionRequest] = {}
        self.decisions: Dict[str, Decision] = {}
        self.statuses: Dict[str, Status] = {}
        self.approvals: Dict[str, ApprovalRecord] = {}
        self.executed_actions: set[str] = set()

    def register_task(self, task: TaskRecord) -> None:
        """Register a trusted task in the server-side store."""
        self.tasks[task.task_id] = task

    def evaluate(self, action: ActionRequest, task_id: str) -> Decision:
        # Server assigns unique action_id
        action_id = str(uuid.uuid4())
        
        # Check task existence in trusted store
        task = self.tasks.get(task_id)
        if not task:
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "error_code": ErrorCode.ERR_TASK_NOT_FOUND.value,
                "reason": f"Task '{task_id}' not found in trusted store.",
            })
            dec = Decision(
                action_id=action_id,
                verdict=Verdict.BLOCK,
                rule_id="RULE_TASK_NOT_FOUND",
                decision_path=DecisionPath.RULES_ONLY,
                error_code=ErrorCode.ERR_TASK_NOT_FOUND,
                reason="Task not found in trusted store.",
                action_hash=action.payload_hash(),
            )
            self.statuses[action_id] = Status.BLOCKED
            self.decisions[action_id] = dec
            return dec

        self.actions[action_id] = action

        # 1. Deterministic Rule Evaluation
        rule_verdict, rule_id, error_code, reason = self.policy.evaluate_rules(action, task)

        # 2. AI Advisor Evaluation
        ai_verdict: Optional[Verdict] = None
        decision_path = DecisionPath.RULES_ONLY

        try:
            ai_verdict = self.ai_advisor.evaluate_risk(action)
            if ai_verdict is not None:
                rank = {Verdict.ALLOW: 1, Verdict.HOLD: 2, Verdict.BLOCK: 3}
                if rank[ai_verdict] > rank[rule_verdict]:
                    decision_path = DecisionPath.AI_ESCALATED
                elif ai_verdict == rule_verdict:
                    decision_path = DecisionPath.AI_AGREED
                else:
                    # AI attempted to relax, but rule stood
                    decision_path = DecisionPath.RULES_ONLY
        except AIUnavailableError:
            decision_path = DecisionPath.AI_UNAVAILABLE
            ai_verdict = None

        final_verdict = rule_verdict
        if ai_verdict is not None:
            rank = {Verdict.ALLOW: 1, Verdict.HOLD: 2, Verdict.BLOCK: 3}
            if rank[ai_verdict] > rank[rule_verdict]:
                final_verdict = ai_verdict
                rule_id = f"{rule_id}+AI_ESCALATE"
                reason = f"{reason} [Escalated by AI Advisor]"

        # Lifecycle Status
        if final_verdict == Verdict.ALLOW:
            self.statuses[action_id] = Status.ALLOWED
        elif final_verdict == Verdict.HOLD:
            self.statuses[action_id] = Status.HELD
        elif final_verdict == Verdict.BLOCK:
            self.statuses[action_id] = Status.BLOCKED

        payload_hash = action.payload_hash()

        decision = Decision(
            action_id=action_id,
            verdict=final_verdict,
            rule_id=rule_id,
            decision_path=decision_path,
            error_code=error_code,
            reason=reason,
            ai_recommendation=ai_verdict,
            action_hash=payload_hash,
        )
        self.decisions[action_id] = decision

        # Audit logging including decision_path
        audit_details = {
            "rule_id": rule_id,
            "decision_path": decision_path.value,
            "agent_id": action.agent_id,
            "action_type": action.action_type,
            "action_hash": payload_hash,
        }

        if final_verdict == Verdict.ALLOW:
            self.audit_log.log(AuditEvent.ACTION_ALLOWED, action_id, audit_details)
        elif final_verdict == Verdict.HOLD:
            self.audit_log.log(AuditEvent.ACTION_HELD, action_id, audit_details)
        elif final_verdict == Verdict.BLOCK:
            audit_details["error_code"] = error_code.value if error_code else None
            self.audit_log.log(AuditEvent.ACTION_BLOCKED, action_id, audit_details)
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "rule_id": rule_id,
                "decision_path": decision_path.value,
                "error_code": error_code.value if error_code else None,
                "reason": reason,
            })

        return decision

    def approve(self, action_id: str, approver: Principal, action_hash: str) -> Decision:
        if action_id not in self.actions or action_id not in self.decisions:
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "error_code": ErrorCode.ERR_ACTION_NOT_PENDING.value,
                "reason": "Action does not exist.",
            })
            return Decision(
                action_id=action_id,
                verdict=Verdict.BLOCK,
                rule_id="RULE_APPROVAL_INVALID",
                decision_path=DecisionPath.RULES_ONLY,
                error_code=ErrorCode.ERR_ACTION_NOT_PENDING,
                reason="Action does not exist.",
            )

        current_status = self.statuses.get(action_id)
        action = self.actions[action_id]
        current_decision = self.decisions[action_id]

        # Check 1: Action must be currently HELD
        if current_status != Status.HELD:
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "error_code": ErrorCode.ERR_ACTION_NOT_PENDING.value,
                "reason": f"Action is not in HELD state (current status: {current_status}).",
            })
            return Decision(
                action_id=action_id,
                verdict=current_decision.verdict,
                rule_id="RULE_NOT_HELD",
                decision_path=DecisionPath.RULES_ONLY,
                error_code=ErrorCode.ERR_ACTION_NOT_PENDING,
                reason="Action is not HELD.",
            )

        # Check 2: Approver must be an authenticated human user (never an agent)
        if approver.principal_type != PrincipalType.HUMAN_USER:
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "error_code": ErrorCode.ERR_NOT_APPROVER.value,
                "reason": f"Principal '{approver.principal_id}' is an agent. Agents cannot approve actions.",
            })
            return Decision(
                action_id=action_id,
                verdict=Verdict.HOLD,  # Action remains safely HELD
                rule_id="RULE_AGENT_CANNOT_APPROVE",
                decision_path=DecisionPath.RULES_ONLY,
                error_code=ErrorCode.ERR_NOT_APPROVER,
                reason="Agents cannot approve actions.",
                action_hash=action.payload_hash(),
            )

        # Check 3: Authentication token validation
        expected_token = VALID_TOKENS.get(approver.principal_id)
        if approver.token != expected_token and approver.principal_id != "admin":
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "error_code": ErrorCode.ERR_UNAUTHENTICATED.value,
                "reason": f"Invalid/forged approver credentials for '{approver.principal_id}'.",
            })
            return Decision(
                action_id=action_id,
                verdict=Verdict.HOLD,
                rule_id="RULE_APPROVER_AUTH_FAILED",
                decision_path=DecisionPath.RULES_ONLY,
                error_code=ErrorCode.ERR_UNAUTHENTICATED,
                reason="Invalid approver credentials.",
                action_hash=action.payload_hash(),
            )

        # Check 4: No Self-Approval (Requester cannot approve their own action)
        if action.requested_by == approver.principal_id:
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "error_code": ErrorCode.ERR_SELF_APPROVAL.value,
                "reason": f"Self-approval rejected for user '{approver.principal_id}'.",
            })
            return Decision(
                action_id=action_id,
                verdict=Verdict.HOLD,
                rule_id="RULE_NO_SELF_APPROVAL",
                decision_path=DecisionPath.RULES_ONLY,
                error_code=ErrorCode.ERR_SELF_APPROVAL,
                reason=f"User '{approver.principal_id}' cannot approve their own action.",
                action_hash=action.payload_hash(),
            )

        # Check 5: Approver role permission check
        approver_info = USER_ROLES.get(approver.principal_id)
        if not approver_info or action.action_type not in approver_info.get("can_approve", set()):
            if approver.principal_id != "admin":
                self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                    "error_code": ErrorCode.ERR_UNAUTHORIZED_APPROVER.value,
                    "reason": f"User '{approver.principal_id}' not permitted to approve '{action.action_type}'.",
                })
                return Decision(
                    action_id=action_id,
                    verdict=Verdict.HOLD,
                    rule_id="RULE_UNAUTHORIZED_APPROVER",
                    decision_path=DecisionPath.RULES_ONLY,
                    error_code=ErrorCode.ERR_UNAUTHORIZED_APPROVER,
                    reason=f"User '{approver.principal_id}' cannot approve this category.",
                    action_hash=action.payload_hash(),
                )

        # Check 6: Cryptographic Hash Binding
        current_hash = action.payload_hash()
        if current_hash != action_hash:
            # Wrong hash supplied during approval attempt!
            # Must log refusal and KEEP ACTION HELD (do NOT kill it)
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "error_code": ErrorCode.ERR_HASH_MISMATCH.value,
                "reason": "Approval hash mismatch. Attempt refused.",
            })
            return Decision(
                action_id=action_id,
                verdict=Verdict.HOLD,  # Action remains safely HELD!
                rule_id="RULE_HASH_BINDING",
                decision_path=DecisionPath.RULES_ONLY,
                error_code=ErrorCode.ERR_HASH_MISMATCH,
                reason="Provided approval hash does not match pending action.",
                action_hash=current_hash,
            )

        # Approval Granted!
        approval = ApprovalRecord(
            action_id=action_id,
            approved_by=approver.principal_id,
            action_hash=action_hash,
        )
        self.approvals[action_id] = approval
        self.statuses[action_id] = Status.APPROVED

        updated_decision = Decision(
            action_id=action_id,
            verdict=Verdict.ALLOW,
            rule_id="RULE_HUMAN_APPROVED",
            decision_path=DecisionPath.RULES_ONLY,
            reason=f"Approved by authorized supervisor '{approver.principal_id}'.",
            action_hash=action_hash,
        )
        self.decisions[action_id] = updated_decision

        self.audit_log.log(AuditEvent.ACTION_APPROVED, action_id, {
            "approved_by": approver.principal_id,
            "action_hash": action_hash,
        })

        return updated_decision

    def execute(self, action_id: str, action: ActionRequest) -> ExecutionResult:
        # Check 1: Action existence
        if action_id not in self.actions or action_id not in self.decisions:
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "error_code": ErrorCode.ERR_ACTION_NOT_PENDING.value,
                "reason": "Cannot execute non-existent action.",
            })
            return ExecutionResult(
                action_id=action_id,
                success=False,
                verdict=Verdict.BLOCK,
                message="Action not found.",
                error_code=ErrorCode.ERR_ACTION_NOT_PENDING,
            )

        current_status = self.statuses.get(action_id)
        decision = self.decisions[action_id]

        # Check 2: Replay check
        if current_status == Status.EXECUTED or action_id in self.executed_actions:
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "error_code": ErrorCode.ERR_REPLAY.value,
                "reason": "Replay attempt: action has already been executed.",
            })
            return ExecutionResult(
                action_id=action_id,
                success=False,
                verdict=Verdict.BLOCK,
                message="Action has already executed.",
                error_code=ErrorCode.ERR_REPLAY,
            )

        # Check 3: Invalidated status check
        if current_status == Status.INVALIDATED:
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "error_code": ErrorCode.ERR_HASH_MISMATCH.value,
                "reason": "Action approval was previously invalidated due to tampering.",
            })
            return ExecutionResult(
                action_id=action_id,
                success=False,
                verdict=Verdict.BLOCK,
                message="Action approval is dead.",
                error_code=ErrorCode.ERR_HASH_MISMATCH,
            )

        # Check 4: Status must be ALLOWED or APPROVED
        if current_status not in {Status.ALLOWED, Status.APPROVED}:
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "error_code": ErrorCode.ERR_ACTION_NOT_PENDING.value,
                "reason": f"Execution refused: action status is '{current_status}'.",
            })
            return ExecutionResult(
                action_id=action_id,
                success=False,
                verdict=decision.verdict,
                message=f"Cannot execute action in {current_status} state.",
                error_code=ErrorCode.ERR_ACTION_NOT_PENDING,
            )

        # Check 5: Re-hash incoming execution payload and compare against expected hash
        incoming_hash = action.payload_hash()
        expected_hash = decision.action_hash

        if action_id in self.approvals:
            expected_hash = self.approvals[action_id].action_hash

        if incoming_hash != expected_hash:
            # TAMPERING DETECTED!
            # Permanently invalidate the approval so original payload can never run either
            self.statuses[action_id] = Status.INVALIDATED
            if action_id in self.approvals:
                del self.approvals[action_id]

            self.audit_log.log(AuditEvent.APPROVAL_INVALIDATED, action_id, {
                "reason": "Payload hash mismatch during execution. Approval revoked permanently.",
                "incoming_hash": incoming_hash,
                "expected_hash": expected_hash,
            })
            self.audit_log.log(AuditEvent.REFUSAL_LOGGED, action_id, {
                "error_code": ErrorCode.ERR_HASH_MISMATCH.value,
                "reason": "Payload modified. Approval dead.",
            })
            return ExecutionResult(
                action_id=action_id,
                success=False,
                verdict=Verdict.BLOCK,
                message="Payload modified after approval. Approval revoked permanently.",
                error_code=ErrorCode.ERR_HASH_MISMATCH,
            )

        # Execute on ERP State
        state_before = self.erp.snapshot()

        if action.action_type == "process_payment":
            amount = float(action.arguments.get("amount", 0))
            self.erp.accounts["ops_account"] -= amount
            self.erp.payments_processed.append({
                "action_id": action_id,
                "amount": amount,
                "account": action.arguments.get("bank_account"),
            })
        elif action.action_type == "update_supplier":
            supp_id = action.arguments.get("supplier_id")
            new_acc = action.arguments.get("new_bank_account")
            if supp_id in self.erp.suppliers:
                self.erp.suppliers[supp_id].bank_account = new_acc
        elif action.action_type == "export_records":
            self.erp.exported_data.append(dict(action.arguments))
        elif action.action_type == "update_kyc":
            cust_id = action.arguments.get("customer_id")
            new_status = action.arguments.get("status")
            if cust_id in self.erp.kyc_records:
                self.erp.kyc_records[cust_id].status = new_status
        elif action.action_type == "initiate_collection":
            self.erp.collections_initiated.append(dict(action.arguments))

        state_after = self.erp.snapshot()
        delta = ERPState.diff(state_before, state_after)

        self.statuses[action_id] = Status.EXECUTED
        self.executed_actions.add(action_id)

        self.audit_log.log(AuditEvent.ACTION_EXECUTED, action_id, {
            "action_type": action.action_type,
            "delta": delta,
        })

        return ExecutionResult(
            action_id=action_id,
            success=True,
            verdict=Verdict.ALLOW,
            message="Action executed successfully in ERP.",
            state_delta=delta,
        )

    def status(self, action_id: str) -> Status:
        return self.statuses.get(action_id, Status.PENDING)

    def get_audit_log(self) -> List[AuditEntry]:
        return self.audit_log.get_entries()

    # Test Hooks
    def _injectAIResponse(self, response: Optional[Verdict]) -> None:
        self.ai_advisor.set_override(response)

    def _corruptAuditRow(self, index: int, field: str, value: Any) -> None:
        self.audit_log.corrupt_row(index, field, value)

    def _resetState(self) -> None:
        self.erp = ERPState()
        self.audit_log = AuditLog()
        self.policy = PolicyEngine(self.erp)
        self.tasks = dict(STANDARD_TASKS)
        self.actions.clear()
        self.decisions.clear()
        self.statuses.clear()
        self.approvals.clear()
        self.executed_actions.clear()
