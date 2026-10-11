"""Deterministic Policy Engine enforcing Co-op Bank Fintech ERP rules."""

from __future__ import annotations
from typing import Optional, Set
from src.types import (
    ActionRequest,
    TaskRecord,
    Verdict,
    ErrorCode,
    Decision,
)
from src.erp_state import ERPState


# Allowed Agents
VALID_AGENTS: Set[str] = {
    "agent-001",  # dispute
    "agent-002",  # kyc
    "agent-003",  # collections
    "agent-004",  # admin
}

# Supported Action Types
VALID_ACTIONS: Set[str] = {
    "process_payment",
    "update_supplier",
    "export_records",
    "update_kyc",
    "initiate_collection",
    "create_user",
    "modify_policy",
    "send_outbound",
}

# Role permissions
USER_ROLES = {
    "riya": {"role": "dispute_operator", "can_request": {"process_payment", "update_supplier"}, "can_approve": {"update_kyc", "initiate_collection"}},
    "karan": {"role": "kyc_officer", "can_request": {"update_kyc", "export_records"}, "can_approve": {"process_payment", "initiate_collection"}},
    "meera": {"role": "collections_officer", "can_request": {"initiate_collection", "export_records"}, "can_approve": {"process_payment", "update_kyc"}},
    "admin": {"role": "admin_officer", "can_request": VALID_ACTIONS, "can_approve": VALID_ACTIONS},
}


class PolicyEngine:
    def __init__(self, erp_state: ERPState):
        self.erp = erp_state

    def evaluate_rules(self, action: ActionRequest, task: TaskRecord) -> tuple[Verdict, str, Optional[ErrorCode], str]:
        """
        Evaluate deterministic rules in strict order.
        Returns: (verdict, rule_id, error_code, reason)
        """
        # Rule 1: Agent Allowlist
        if action.agent_id not in VALID_AGENTS:
            return (
                Verdict.BLOCK,
                "RULE_AGENT_ALLOWLIST",
                ErrorCode.ERR_UNKNOWN_AGENT,
                f"Agent '{action.agent_id}' is not in the authorized agent registry."
            )

        # Rule 2: Action Type Allowlist
        if action.action_type not in VALID_ACTIONS:
            return (
                Verdict.BLOCK,
                "RULE_ACTION_ALLOWLIST",
                ErrorCode.ERR_UNKNOWN_ACTION,
                f"Action '{action.action_type}' is unrecognized by gateway policy."
            )

        # Rule 3: Task Scope Check (Enforces TaskRecord boundaries)
        # Check that the assigned agent matches
        if task.assigned_agent != action.agent_id:
            return (
                Verdict.BLOCK,
                "RULE_TASK_SCOPE_ASSIGNMENT",
                ErrorCode.ERR_TASK_SCOPE_VIOLATION,
                f"Agent '{action.agent_id}' not assigned to Task '{task.task_id}' (expected {task.assigned_agent})."
            )

        # Check that action operation is in task allowed_operations
        if action.action_type not in task.allowed_operations:
            return (
                Verdict.BLOCK,
                "RULE_TASK_SCOPE",
                ErrorCode.ERR_TASK_SCOPE_VIOLATION,
                f"Action '{action.action_type}' is outside the authorized operations for task '{task.task_id}'."
            )

        # Rule 4: Administrative Actions (create_user, modify_policy)
        if action.action_type in {"create_user", "modify_policy"}:
            if action.requested_by != "admin":
                return (
                    Verdict.BLOCK,
                    "RULE_ADMIN_PRIVILEGE",
                    ErrorCode.ERR_BLOCKED_BY_POLICY,
                    f"Action '{action.action_type}' requires admin officer authorization."
                )

        # Rule 5: Argument Origin & Verification Checks
        if action.action_type == "process_payment":
            target_account = action.arguments.get("bank_account", "")
            supplier_id = action.arguments.get("supplier_id")
            
            # Check if bank_account is verified in master records
            verified_in_erp = False
            if supplier_id and supplier_id in self.erp.suppliers:
                if self.erp.suppliers[supplier_id].bank_account == target_account and self.erp.suppliers[supplier_id].verified:
                    verified_in_erp = True

            # If the account is NOT verified in the ERP supplier master, it requires explicit trusted provenance
            if not verified_in_erp:
                has_trusted_provenance = any(c.trusted for c in action.context_sources)
                if not has_trusted_provenance:
                    return (
                        Verdict.HOLD,
                        "RULE_ARG_ORIGIN",
                        ErrorCode.ERR_UNTRUSTED_ARGUMENT_ORIGIN,
                        "Target bank account does not match verified supplier master and lacks trusted provenance."
                    )

        # Rule 6: Action-Specific Thresholds
        if action.action_type == "process_payment":
            amount = float(action.arguments.get("amount", 0))
            if amount <= 10000.0:
                return Verdict.ALLOW, "RULE_THRESHOLD_PAYMENT_AUTO", None, "Payment amount within auto-approval threshold (<= ₹10,000)."
            elif amount <= 100000.0:
                return Verdict.HOLD, "RULE_THRESHOLD_PAYMENT_HOLD", None, "Payment requires human approval (₹10,001 - ₹1,00,000)."
            else:
                return Verdict.BLOCK, "RULE_THRESHOLD_PAYMENT_BLOCK", ErrorCode.ERR_BLOCKED_BY_POLICY, "Payment amount exceeds maximum gateway limit (> ₹1,00,000)."

        elif action.action_type == "export_records":
            target_entity = str(action.arguments.get("target_entity", ""))
            fields = action.arguments.get("fields", [])
            record_count = int(action.arguments.get("record_count", 0))

            # Sensitive fields or entities (SSN, salary, passwords, KYC identity)
            sensitive_fields = {"salary", "ssn", "aadhaar", "pan", "password_hash", "pin"}
            if any(str(f).lower() in sensitive_fields for f in fields) or target_entity in {"salaries", "credentials", "auth_tokens"}:
                return (
                    Verdict.BLOCK,
                    "RULE_SENSITIVE_FIELD_EXPORT_BLOCKED",
                    ErrorCode.ERR_BLOCKED_BY_POLICY,
                    "Export of sensitive employee/identity/credential fields is prohibited by policy."
                )

            if record_count <= 25:
                return Verdict.ALLOW, "RULE_THRESHOLD_EXPORT_AUTO", None, "Export record volume within auto-approval limit (<= 25)."
            elif record_count <= 1000:
                return Verdict.HOLD, "RULE_THRESHOLD_EXPORT_HOLD", None, "Bulk export requires human supervisor approval (26 - 1,000 records)."
            else:
                return Verdict.BLOCK, "RULE_THRESHOLD_EXPORT_BLOCK", ErrorCode.ERR_BLOCKED_BY_POLICY, "Mass data export volume blocked by policy (> 1,000 records)."

        elif action.action_type == "send_outbound":
            return (
                Verdict.BLOCK,
                "RULE_OUTBOUND_COMMUNICATION_BLOCKED",
                ErrorCode.ERR_BLOCKED_BY_POLICY,
                "Outbound transmission of enterprise messages or data is prohibited by gateway policy."
            )

        elif action.action_type == "update_supplier":
            return Verdict.HOLD, "RULE_MANDATORY_HOLD_SUPPLIER", None, "Supplier master modifications mandate human verification."

        elif action.action_type == "update_kyc":
            return Verdict.HOLD, "RULE_MANDATORY_HOLD_KYC", None, "Customer KYC state changes mandate human verification."

        elif action.action_type == "initiate_collection":
            amount = float(action.arguments.get("amount", 0))
            if amount <= 10000.0:
                return Verdict.ALLOW, "RULE_THRESHOLD_COLLECTION_AUTO", None, "Collection initiation within automated threshold (<= ₹10,000)."
            else:
                return Verdict.HOLD, "RULE_THRESHOLD_COLLECTION_HOLD", None, "High-value collection requires supervisor review (> ₹10,000)."

        # Fallback default
        return Verdict.HOLD, "RULE_DEFAULT_HOLD", None, "Action flagged for human verification by default."
