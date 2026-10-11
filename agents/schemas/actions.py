from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from agents.provenance.fingerprint import calculate_action_fingerprint

class ActionType(str, Enum):
    # HR Actions
    HR_GET_PROFILE = "hr.get_profile"
    HR_GET_DIRECTORY = "hr.get_directory"
    
    # Leave Actions
    LEAVE_CREATE = "leave.create"
    LEAVE_GET_HISTORY = "leave.get_history"
    
    # Finance Actions
    EXPENSE_SUBMIT = "expense.submit"
    EXPENSE_GET_LIST = "expense.get_list"
    EXPENSE_APPROVE = "expense.approve"

# Payload Models
class LeaveCreatePayload(BaseModel):
    employee_id: str = Field(..., min_length=1, description="Verified requester employee ID")
    leave_type: str = Field(..., description="Leave type: ANNUAL, SICK, CASUAL, etc.")
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Start date in YYYY-MM-DD")
    end_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="End date in YYYY-MM-DD")
    reason: str = Field(..., min_length=2, max_length=500, description="Reason for leave")

    @field_validator("leave_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid = {"ANNUAL", "SICK", "CASUAL", "MATERNITY", "PATERNITY", "UNPAID"}
        v_upper = v.strip().upper()
        if v_upper not in valid:
            raise ValueError(f"Invalid leave type '{v}'. Allowed: {', '.join(sorted(valid))}")
        return v_upper

class ExpenseSubmitPayload(BaseModel):
    employee_id: str = Field(..., min_length=1, description="Verified requester employee ID")
    amount: float = Field(..., gt=0, description="Claim amount, must be greater than zero")
    currency: str = Field(default="INR", min_length=3, max_length=3, description="Currency code (e.g. INR, USD)")
    category: str = Field(..., description="Category: TRAVEL, MEALS, EQUIPMENT, SOFTWARE, OFFICE, MISC")
    description: str = Field(..., min_length=3, max_length=500, description="Expense description")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid = {"TRAVEL", "MEALS", "EQUIPMENT", "SOFTWARE", "OFFICE", "TRAINING", "MISC"}
        v_upper = v.strip().upper()
        if v_upper not in valid:
            raise ValueError(f"Invalid expense category '{v}'. Allowed: {', '.join(sorted(valid))}")
        return v_upper

class ExpenseApprovePayload(BaseModel):
    expense_id: str = Field(..., min_length=1, description="Target expense claim ID to approve")
    approver_id: str = Field(..., min_length=1, description="Verified manager/approver employee ID")
    decision: str = Field(..., description="Decision: APPROVE or REJECT")
    notes: Optional[str] = Field(None, max_length=500, description="Optional approver notes")

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v: str) -> str:
        v_upper = v.strip().upper()
        if v_upper not in {"APPROVE", "REJECT"}:
            raise ValueError("Decision must be 'APPROVE' or 'REJECT'")
        return v_upper

class ProfileQueryPayload(BaseModel):
    employee_id: str = Field(..., min_length=1)

class DirectoryQueryPayload(BaseModel):
    query: Optional[str] = None
    department: Optional[str] = None

class LeaveHistoryQueryPayload(BaseModel):
    employee_id: str = Field(..., min_length=1)

class ExpenseListQueryPayload(BaseModel):
    employee_id: str = Field(..., min_length=1)

ACTION_PAYLOAD_MAP = {
    ActionType.HR_GET_PROFILE: ProfileQueryPayload,
    ActionType.HR_GET_DIRECTORY: DirectoryQueryPayload,
    ActionType.LEAVE_CREATE: LeaveCreatePayload,
    ActionType.LEAVE_GET_HISTORY: LeaveHistoryQueryPayload,
    ActionType.EXPENSE_SUBMIT: ExpenseSubmitPayload,
    ActionType.EXPENSE_GET_LIST: ExpenseListQueryPayload,
    ActionType.EXPENSE_APPROVE: ExpenseApprovePayload,
}

class ProposedAction(BaseModel):
    action_type: ActionType
    target_resource: str
    parameters: Dict[str, Any]
    requester_id: str
    action_fingerprint: str
    description: str

    @classmethod
    def create_and_sign(
        cls,
        action_type: ActionType,
        target_resource: str,
        parameters: Dict[str, Any],
        requester_id: str,
        description: str
    ) -> "ProposedAction":
        fingerprint = calculate_action_fingerprint(
            action_type=action_type.value,
            target_resource=target_resource,
            parameters=parameters,
            requester_id=requester_id
        )
        return cls(
            action_type=action_type,
            target_resource=target_resource,
            parameters=parameters,
            requester_id=requester_id,
            action_fingerprint=fingerprint,
            description=description
        )

def validate_action_proposal(action_type_str: str, raw_params: Dict[str, Any]) -> BaseModel:
    """
    Validates that action_type_str is on the strict allowlist and parameters conform
    to the corresponding Pydantic schema.
    """
    try:
        action_type = ActionType(action_type_str)
    except ValueError:
        raise ValueError(f"Action '{action_type_str}' is NOT in the allowed action catalog.")
    
    schema_cls = ACTION_PAYLOAD_MAP.get(action_type)
    if not schema_cls:
        raise ValueError(f"No schema mapping registered for action {action_type}.")
        
    return schema_cls(**raw_params)
