import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from agents.schemas.erp import (
    ERPUserRole,
    ERPUserContext,
    LeaveRecord,
    LeaveStatus,
    ExpenseRecord,
    ExpenseStatus,
    ERPExecutionResponse,
)
from agents.schemas.actiongate import (
    DecisionType,
    RiskLevel,
    ActionGateRequest,
    ActionGateDecision,
    HoldDetails,
    ActionGateApprovalSubmission,
)
from agents.provenance.fingerprint import calculate_action_fingerprint

class MockERP:
    """
    High-fidelity simulated ERP business backend with in-memory state.
    Used for local execution, contract verification, and standalone demo cases.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.employees: Dict[str, Dict[str, Any]] = {
            "EMP-001": {
                "employee_id": "EMP-001",
                "name": "Rahul Sharma",
                "email": "rahul.sharma@corp.mini-erp.com",
                "role": ERPUserRole.EMPLOYEE,
                "department": "Engineering",
                "manager_id": "MGR-002",
                "designation": "Senior Software Engineer",
            },
            "EMP-002": {
                "employee_id": "EMP-002",
                "name": "Priya Patel",
                "email": "priya.patel@corp.mini-erp.com",
                "role": ERPUserRole.EMPLOYEE,
                "department": "Sales",
                "manager_id": "MGR-002",
                "designation": "Sales Executive",
            },
            "MGR-002": {
                "employee_id": "MGR-002",
                "name": "Vikram Malhotra",
                "email": "vikram.malhotra@corp.mini-erp.com",
                "role": ERPUserRole.MANAGER,
                "department": "Engineering",
                "manager_id": "DIR-001",
                "designation": "Engineering Manager",
            },
            "FIN-003": {
                "employee_id": "FIN-003",
                "name": "Anita Desai",
                "email": "anita.desai@corp.mini-erp.com",
                "role": ERPUserRole.FINANCE_ADMIN,
                "department": "Finance",
                "manager_id": "DIR-001",
                "designation": "Finance Lead",
            },
        }

        self.leaves: List[Dict[str, Any]] = [
            {
                "leave_id": "LV-1001",
                "employee_id": "EMP-001",
                "leave_type": "ANNUAL",
                "start_date": "2026-09-10",
                "end_date": "2026-09-12",
                "days_count": 3.0,
                "reason": "Family vacation",
                "status": LeaveStatus.APPROVED.value,
            }
        ]

        self.expenses: Dict[str, Dict[str, Any]] = {
            "EXP-101": {
                "expense_id": "EXP-101",
                "employee_id": "EMP-001",
                "amount": 50000.0,
                "currency": "INR",
                "category": "EQUIPMENT",
                "description": "High-end laptop monitor and accessories",
                "status": ExpenseStatus.PENDING.value,
                "approver_id": None,
                "created_at": "2026-10-01T10:00:00Z",
            },
            "EXP-102": {
                "expense_id": "EXP-102",
                "employee_id": "EMP-002",
                "amount": 4500.0,
                "currency": "INR",
                "category": "TRAVEL",
                "description": "Client meeting cab fare",
                "status": ExpenseStatus.PENDING.value,
                "approver_id": None,
                "created_at": "2026-10-05T12:30:00Z",
            },
        }
        self.is_down: bool = False

    def get_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        if self.is_down:
            raise ConnectionError("ERP service unavailable")
        return self.employees.get(employee_id)

    def search_directory(self, query: Optional[str] = None, department: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.is_down:
            raise ConnectionError("ERP service unavailable")
        results = list(self.employees.values())
        if department:
            results = [e for e in results if e["department"].lower() == department.lower()]
        if query:
            q = query.lower()
            results = [e for e in results if q in e["name"].lower() or q in e["email"].lower() or q in e["designation"].lower()]
        return results

    def get_leave_history(self, employee_id: str) -> List[Dict[str, Any]]:
        if self.is_down:
            raise ConnectionError("ERP service unavailable")
        return [l for l in self.leaves if l["employee_id"] == employee_id]

    def create_leave(self, employee_id: str, leave_type: str, start_date: str, end_date: str, reason: str) -> ERPExecutionResponse:
        if self.is_down:
            raise ConnectionError("ERP service unavailable")
        
        leave_id = f"LV-{1000 + len(self.leaves) + 1}"
        record = {
            "leave_id": leave_id,
            "employee_id": employee_id,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "days_count": 1.0,
            "reason": reason,
            "status": LeaveStatus.PENDING.value,
        }
        self.leaves.append(record)
        return ERPExecutionResponse(
            success=True,
            action_type="leave.create",
            message=f"Leave request {leave_id} successfully created and submitted for manager approval.",
            data=record,
        )

    def get_expenses(self, employee_id: str) -> List[Dict[str, Any]]:
        if self.is_down:
            raise ConnectionError("ERP service unavailable")
        return [exp for exp in self.expenses.values() if exp["employee_id"] == employee_id]

    def submit_expense(self, employee_id: str, amount: float, currency: str, category: str, description: str) -> ERPExecutionResponse:
        if self.is_down:
            raise ConnectionError("ERP service unavailable")
        
        exp_id = f"EXP-{len(self.expenses) + 101}"
        record = {
            "expense_id": exp_id,
            "employee_id": employee_id,
            "amount": amount,
            "currency": currency,
            "category": category,
            "description": description,
            "status": ExpenseStatus.PENDING.value,
            "approver_id": None,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.expenses[exp_id] = record
        return ERPExecutionResponse(
            success=True,
            action_type="expense.submit",
            message=f"Expense claim {exp_id} submitted for {currency} {amount:,.2f}.",
            data=record,
        )

    def approve_expense(self, expense_id: str, approver_id: str, decision: str, notes: Optional[str] = None) -> ERPExecutionResponse:
        if self.is_down:
            raise ConnectionError("ERP service unavailable")
        
        expense = self.expenses.get(expense_id)
        if not expense:
            return ERPExecutionResponse(
                success=False,
                action_type="expense.approve",
                message=f"Expense record {expense_id} not found in ERP.",
                error_code="RECORD_NOT_FOUND",
            )
        
        new_status = ExpenseStatus.APPROVED.value if decision.upper() == "APPROVE" else ExpenseStatus.REJECTED.value
        expense["status"] = new_status
        expense["approver_id"] = approver_id
        expense["decision_notes"] = notes
        
        return ERPExecutionResponse(
            success=True,
            action_type="expense.approve",
            message=f"Expense {expense_id} has been marked as {new_status}.",
            data=expense,
        )

class MockActionGate:
    """
    High-fidelity deterministic ActionGate Authorization Engine.
    Implements risk scoring, ALLOW/BLOCK/HOLD decisions, exact-action fingerprint matching,
    and out-of-band approval integration with ERP.
    """
    def __init__(self, erp_backend: Optional[MockERP] = None):
        self.erp = erp_backend or MockERP()
        self.reset()

    def reset(self):
        self.approved_registry: Dict[str, ActionGateApprovalSubmission] = {}
        self.decisions_audit: Dict[str, ActionGateDecision] = {}
        self.is_down: bool = False

    def register_erp_approval(
        self,
        decision_id: str,
        approver_id: str,
        approver_role: str,
        action_fingerprint: str,
        status: str = "APPROVED",
        notes: Optional[str] = None
    ) -> ActionGateApprovalSubmission:
        submission = ActionGateApprovalSubmission(
            decision_id=decision_id,
            approver_id=approver_id,
            approver_role=approver_role,
            action_fingerprint=action_fingerprint,
            status=status,
            notes=notes,
        )
        self.approved_registry[action_fingerprint] = submission
        return submission

    def evaluate(self, request: ActionGateRequest) -> ActionGateDecision:
        if self.is_down:
            raise ConnectionError("ActionGate service unavailable")

        decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"
        reasons = []

        if request.action_type in ["hr.get_profile", "hr.get_directory", "leave.get_history", "expense.get_list"]:
            decision = ActionGateDecision(
                decision_id=decision_id,
                request_id=request.request_id,
                decision=DecisionType.ALLOW,
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                reasons=["Read-only operation permitted for authenticated user."],
                action_fingerprint=request.action_fingerprint,
            )
            self.decisions_audit[decision_id] = decision
            return decision

        if request.action_type == "leave.create":
            decision = ActionGateDecision(
                decision_id=decision_id,
                request_id=request.request_id,
                decision=DecisionType.ALLOW,
                risk_score=0.1,
                risk_level=RiskLevel.LOW,
                reasons=["Employee permitted to request leave for self."],
                action_fingerprint=request.action_fingerprint,
            )
            self.decisions_audit[decision_id] = decision
            return decision

        if request.action_type == "expense.submit":
            amount = request.parameters.get("amount", 0)
            risk = 0.2 if amount <= 10000 else 0.4
            decision = ActionGateDecision(
                decision_id=decision_id,
                request_id=request.request_id,
                decision=DecisionType.ALLOW,
                risk_score=risk,
                risk_level=RiskLevel.LOW if risk <= 0.2 else RiskLevel.MEDIUM,
                reasons=["Expense claim submission permitted; subject to manager review upon creation."],
                action_fingerprint=request.action_fingerprint,
            )
            self.decisions_audit[decision_id] = decision
            return decision

        if request.action_type == "expense.approve":
            target_id = request.parameters.get("expense_id") or request.target_resource
            expense = self.erp.expenses.get(target_id)
            
            # Segregation of duties: self-approval blocked
            if expense and expense.get("employee_id") == request.requester_id:
                reasons.append("Segregation of Duties Violation: Employee cannot approve their own expense claim.")
                decision = ActionGateDecision(
                    decision_id=decision_id,
                    request_id=request.request_id,
                    decision=DecisionType.BLOCK,
                    risk_score=1.0,
                    risk_level=RiskLevel.CRITICAL,
                    reasons=reasons,
                    action_fingerprint=request.action_fingerprint,
                )
                self.decisions_audit[decision_id] = decision
                return decision

            # Check exact-action approval registry
            stored_approval = self.approved_registry.get(request.action_fingerprint)
            if stored_approval and stored_approval.status == "APPROVED":
                reasons.append(
                    f"Verified exact-action approval from authorized manager {stored_approval.approver_id} "
                    f"via ERP workflow (Decision {stored_approval.decision_id})."
                )
                decision = ActionGateDecision(
                    decision_id=decision_id,
                    request_id=request.request_id,
                    decision=DecisionType.ALLOW,
                    risk_score=0.2,
                    risk_level=RiskLevel.LOW,
                    reasons=reasons,
                    action_fingerprint=request.action_fingerprint,
                )
                self.decisions_audit[decision_id] = decision
                return decision

            # Out-of-band manager sign-off required -> HOLD
            reasons.append(
                "High-value expense approval requires out-of-band manager sign-off via ERP approval workflow."
            )
            hold = HoldDetails(
                approval_workflow="ERP_MANAGER_APPROVAL",
                required_role="MANAGER",
                workflow_url=f"/erp/approvals/expenses/{target_id}",
                instructions="Direct user to the ERP Approval Portal. Conversational approvals are not recognized."
            )
            decision = ActionGateDecision(
                decision_id=decision_id,
                request_id=request.request_id,
                decision=DecisionType.HOLD,
                risk_score=0.6,
                risk_level=RiskLevel.HIGH,
                reasons=reasons,
                action_fingerprint=request.action_fingerprint,
                approval_required_role="MANAGER",
                hold_details=hold,
            )
            self.decisions_audit[decision_id] = decision
            return decision

        decision = ActionGateDecision(
            decision_id=decision_id,
            request_id=request.request_id,
            decision=DecisionType.BLOCK,
            risk_score=0.9,
            risk_level=RiskLevel.CRITICAL,
            reasons=[f"Action type '{request.action_type}' is not authorized."],
            action_fingerprint=request.action_fingerprint,
        )
        self.decisions_audit[decision_id] = decision
        return decision
