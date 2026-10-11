import pytest
from agents.graph.state import ChatState
from agents.schemas.actiongate import DecisionType

def test_hr_profile_retrieval(orchestrator, employee_user):
    state: ChatState = {
        "user_message": "View my profile details",
        "user_context": employee_user,
    }
    result = orchestrator.invoke(state)
    assert result["status"] == "SUCCESS"
    assert result["actiongate_decision"].decision == DecisionType.ALLOW
    assert "Rahul Sharma" in result["final_response"]
    assert "EMP-001" in result["final_response"]
    assert "Engineering" in result["final_response"]

def test_hr_directory_lookup(orchestrator, employee_user):
    state: ChatState = {
        "user_message": "Search directory for engineering team",
        "user_context": employee_user,
    }
    result = orchestrator.invoke(state)
    assert result["status"] == "SUCCESS"
    assert result["actiongate_decision"].decision == DecisionType.ALLOW
    assert "Company Directory" in result["final_response"]
    assert "Vikram Malhotra" in result["final_response"]

def test_leave_history_retrieval(orchestrator, employee_user):
    state: ChatState = {
        "user_message": "Show my leave history",
        "user_context": employee_user,
    }
    result = orchestrator.invoke(state)
    assert result["status"] == "SUCCESS"
    assert result["actiongate_decision"].decision == DecisionType.ALLOW
    assert "LV-1001" in result["final_response"]

def test_expense_list_retrieval(orchestrator, employee_user):
    state: ChatState = {
        "user_message": "List my submitted expense claims",
        "user_context": employee_user,
    }
    result = orchestrator.invoke(state)
    assert result["status"] == "SUCCESS"
    assert result["actiongate_decision"].decision == DecisionType.ALLOW
    assert "EXP-101" in result["final_response"]

def test_expense_submit_missing_fields(orchestrator, employee_user):
    state: ChatState = {
        "user_message": "Submit expense claim for ₹1,200",
        "user_context": employee_user,
    }
    result = orchestrator.invoke(state)
    assert result["status"] == "NEEDS_CLARIFICATION"
    assert "category" in result["missing_fields"]
    assert "description" in result["missing_fields"]
    assert "missing details" in result["final_response"]

def test_expense_submit_successful(orchestrator, employee_user, mock_erp):
    initial_exp_count = len(mock_erp.expenses)
    state: ChatState = {
        "user_message": "Submit expense claim of ₹3,500 under MEALS for client project dinner",
        "user_context": employee_user,
    }
    result = orchestrator.invoke(state)
    assert result["status"] == "SUCCESS"
    assert result["actiongate_decision"].decision == DecisionType.ALLOW
    assert len(mock_erp.expenses) == initial_exp_count + 1
    assert "Expense Claim Submitted Successfully" in result["final_response"]

def test_erp_backend_outage_fails_closed(orchestrator, employee_user, mock_erp):
    mock_erp.is_down = True
    state: ChatState = {
        "user_message": "View my profile",
        "user_context": employee_user,
    }
    result = orchestrator.invoke(state)
    assert result["status"] == "ERROR"
    assert "ERP communication failure" in result["final_response"]
