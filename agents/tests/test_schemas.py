import pytest
from agents.schemas.actions import (
    ActionType,
    LeaveCreatePayload,
    ExpenseSubmitPayload,
    validate_action_proposal,
)
from agents.provenance.fingerprint import calculate_action_fingerprint

def test_action_allowlist_valid():
    assert ActionType("leave.create") == ActionType.LEAVE_CREATE
    assert ActionType("expense.submit") == ActionType.EXPENSE_SUBMIT
    assert ActionType("expense.approve") == ActionType.EXPENSE_APPROVE
    assert ActionType("hr.get_profile") == ActionType.HR_GET_PROFILE

def test_action_allowlist_unsupported():
    with pytest.raises(ValueError):
        ActionType("database.raw_query")
    with pytest.raises(ValueError):
        validate_action_proposal("admin.delete_all", {})

def test_leave_create_payload_validation():
    valid_payload = {
        "employee_id": "EMP-001",
        "leave_type": "ANNUAL",
        "start_date": "2026-10-19",
        "end_date": "2026-10-19",
        "reason": "Personal work",
    }
    obj = validate_action_proposal("leave.create", valid_payload)
    assert isinstance(obj, LeaveCreatePayload)
    assert obj.leave_type == "ANNUAL"

    invalid_payload = valid_payload.copy()
    invalid_payload["leave_type"] = "INVALID_TYPE"
    with pytest.raises(ValueError, match="Invalid leave type"):
        validate_action_proposal("leave.create", invalid_payload)

def test_expense_submit_payload_validation():
    valid = {
        "employee_id": "EMP-001",
        "amount": 4500.0,
        "currency": "INR",
        "category": "TRAVEL",
        "description": "Client meeting cab",
    }
    obj = validate_action_proposal("expense.submit", valid)
    assert isinstance(obj, ExpenseSubmitPayload)
    assert obj.amount == 4500.0

    invalid = valid.copy()
    invalid["amount"] = -100.0
    with pytest.raises(ValueError):
        validate_action_proposal("expense.submit", invalid)

def test_deterministic_action_fingerprint():
    params = {"employee_id": "EMP-001", "amount": 50000.0, "category": "EQUIPMENT"}
    
    fp1 = calculate_action_fingerprint("expense.submit", "erp:expense", params, "EMP-001")
    fp2 = calculate_action_fingerprint("expense.submit", "erp:expense", params, "EMP-001")
    assert fp1 == fp2, "Fingerprint should be identical for identical payload"

    tampered_params = params.copy()
    tampered_params["amount"] = 55000.0
    fp_tampered = calculate_action_fingerprint("expense.submit", "erp:expense", tampered_params, "EMP-001")
    assert fp1 != fp_tampered, "Fingerprint must change when parameters are modified"

    fp_tampered_target = calculate_action_fingerprint("expense.submit", "erp:expense:different", params, "EMP-001")
    assert fp1 != fp_tampered_target, "Fingerprint must change when target changes"

    fp_tampered_requester = calculate_action_fingerprint("expense.submit", "erp:expense", params, "EMP-002")
    assert fp1 != fp_tampered_requester, "Fingerprint must change when requester changes"
