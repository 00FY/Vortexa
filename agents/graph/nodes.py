import uuid
from typing import Dict, Any, Optional
from agents.graph.state import ChatState
from agents.schemas.erp import ERPUserContext, ERPExecutionResponse
from agents.schemas.actions import (
    ActionType,
    ProposedAction,
    validate_action_proposal,
)
from agents.provenance.fingerprint import calculate_action_fingerprint
from agents.schemas.actiongate import ActionGateRequest, DecisionType
from agents.router.intent_router import route_request
from agents.specialists.hr_agent import HRAgent
from agents.specialists.leave_agent import LeaveAgent
from agents.specialists.finance_agent import FinanceAgent
from agents.gate_client.actiongate_client import ActionGateClient
from agents.gate_client.erp_client import ERPClient

hr_agent = HRAgent()
leave_agent = LeaveAgent()
finance_agent = FinanceAgent()

def authenticate_and_validate_context(state: ChatState) -> Dict[str, Any]:
    user_context = state.get("user_context")
    if not user_context or not isinstance(user_context, ERPUserContext):
        return {
            "validation_error": "Missing or invalid authenticated ERP session context.",
            "status": "ERROR",
            "final_response": "Authentication error: Verified user session context is required."
        }
    
    req_id = state.get("request_id") or f"REQ-{uuid.uuid4().hex[:8].upper()}"
    sess_id = state.get("session_id") or f"SESS-{uuid.uuid4().hex[:8].upper()}"
    
    return {
        "request_id": req_id,
        "session_id": sess_id,
    }

def classify_intent_and_route(state: ChatState) -> Dict[str, Any]:
    if state.get("validation_error"):
        return {}

    msg = state.get("user_message", "").strip()
    route_meta = route_request(msg)

    if route_meta["is_blocked"]:
        return {
            "intent": route_meta["intent"],
            "validation_error": route_meta["error"],
            "status": "BLOCKED",
            "final_response": route_meta["refusal_message"]
        }

    return {"intent": route_meta["intent"]}

def invoke_specialized_agent(state: ChatState) -> Dict[str, Any]:
    if state.get("validation_error") or state.get("final_response"):
        return {}

    intent = state.get("intent")
    user_msg = state.get("user_message", "")
    user_context = state.get("user_context")
    conv_context = state.get("conversation_context", {})

    if intent == "LEAVE":
        action, clarification, missing = leave_agent.process(user_msg, user_context, conv_context)
    elif intent == "FINANCE":
        action, clarification, missing = finance_agent.process(user_msg, user_context, conv_context)
    elif intent == "HR":
        action, clarification, missing = hr_agent.process(user_msg, user_context, conv_context)
    else:
        return {
            "status": "NEEDS_CLARIFICATION",
            "clarification_message": "I can assist you with HR profile/directory lookup, Leave applications, and Expense management. Please specify your request."
        }

    if clarification:
        return {
            "clarification_message": clarification,
            "missing_fields": missing,
            "status": "NEEDS_CLARIFICATION"
        }

    return {
        "proposed_action": action,
    }

def validate_action_allowlist(state: ChatState) -> Dict[str, Any]:
    if state.get("validation_error") or state.get("clarification_message"):
        return {}

    action = state.get("proposed_action")
    if not action:
        return {
            "validation_error": "No action proposed by agent.",
            "status": "ERROR"
        }

    user_context = state.get("user_context")

    try:
        ActionType(action.action_type)
    except ValueError:
        return {
            "validation_error": f"Action type '{action.action_type}' is not on the permitted allowlist.",
            "status": "ERROR"
        }

    if action.requester_id != user_context.employee_id:
        return {
            "validation_error": "Security violation: Action proposal requester ID does not match authenticated ERP session identity.",
            "status": "BLOCKED"
        }

    try:
        validate_action_proposal(action.action_type.value, action.parameters)
    except Exception as e:
        return {
            "validation_error": f"Action parameter validation failed: {str(e)}",
            "status": "ERROR"
        }

    expected_fingerprint = calculate_action_fingerprint(
        action_type=action.action_type.value,
        target_resource=action.target_resource,
        parameters=action.parameters,
        requester_id=user_context.employee_id
    )
    if action.action_fingerprint != expected_fingerprint:
        return {
            "validation_error": "Security violation: Action fingerprint integrity check failed (proposal tampered).",
            "status": "BLOCKED"
        }

    return {}

def evaluate_with_actiongate(
    state: ChatState,
    actiongate_client: Optional[ActionGateClient] = None
) -> Dict[str, Any]:
    if state.get("validation_error") or state.get("clarification_message"):
        return {}

    action = state.get("proposed_action")
    user_context = state.get("user_context")
    req_id = state.get("request_id")

    client = actiongate_client or ActionGateClient()

    ag_request = ActionGateRequest(
        request_id=req_id,
        action_type=action.action_type.value,
        target_resource=action.target_resource,
        parameters=action.parameters,
        requester_id=user_context.employee_id,
        requester_role=user_context.role.value,
        requester_department=user_context.department,
        action_fingerprint=action.action_fingerprint,
    )

    try:
        decision = client.evaluate_proposal(ag_request)
        return {"actiongate_decision": decision}
    except Exception as e:
        return {
            "outage_error": f"ActionGate authorization service unavailable: {str(e)}",
            "status": "ERROR",
            "final_response": "The requested operation cannot be safely evaluated or completed because the ActionGate authorization service is temporarily unavailable. For security, protected operations remain halted."
        }

def execute_or_handle_decision(
    state: ChatState,
    erp_client: Optional[ERPClient] = None
) -> Dict[str, Any]:
    if state.get("validation_error") or state.get("clarification_message") or state.get("outage_error"):
        return {}

    decision = state.get("actiongate_decision")
    action = state.get("proposed_action")
    user_context = state.get("user_context")
    client = erp_client or ERPClient()

    if not decision:
        return {
            "status": "ERROR",
            "final_response": "Internal error: Missing authorization decision."
        }

    if decision.decision == DecisionType.BLOCK:
        reasons_text = " ".join(decision.reasons)
        return {
            "status": "BLOCKED",
            "final_response": f"Action Prohibited by ActionGate:\n• {reasons_text}\n\nThis operation was blocked in accordance with enterprise authorization policies."
        }

    if decision.decision == DecisionType.HOLD:
        hold_info = decision.hold_details
        workflow_url = hold_info.workflow_url if hold_info else "/erp/approvals"
        reasons_text = " ".join(decision.reasons)
        return {
            "status": "HELD",
            "final_response": (
                f"Action Pending Formal Approval (Decision ID: {decision.decision_id}):\n"
                f"• {reasons_text}\n\n"
                f"Notice: Conversational consent is not recognized as formal authorization. "
                f"Please navigate to the ERP Portal to complete the authorized approval workflow:\n"
                f"👉 [ERP Approval Workflow]({workflow_url})\n\n"
                f"Action Fingerprint: `{decision.action_fingerprint}`"
            )
        }

    if decision.decision == DecisionType.ALLOW:
        try:
            act_type = action.action_type
            params = action.parameters

            if act_type == ActionType.LEAVE_CREATE:
                exec_resp = client.create_leave_request(
                    employee_id=params["employee_id"],
                    leave_type=params["leave_type"],
                    start_date=params["start_date"],
                    end_date=params["end_date"],
                    reason=params["reason"],
                    auth_token=user_context.token
                )
            elif act_type == ActionType.LEAVE_GET_HISTORY:
                leaves = client.get_leave_history(employee_id=params["employee_id"], auth_token=user_context.token)
                exec_resp = ERPExecutionResponse(
                    success=True,
                    action_type="leave.get_history",
                    message=f"Retrieved {len(leaves)} leave records.",
                    data={"leaves": leaves}
                )
            elif act_type == ActionType.EXPENSE_SUBMIT:
                exec_resp = client.submit_expense_claim(
                    employee_id=params["employee_id"],
                    amount=params["amount"],
                    currency=params["currency"],
                    category=params["category"],
                    description=params["description"],
                    auth_token=user_context.token
                )
            elif act_type == ActionType.EXPENSE_GET_LIST:
                expenses = client.get_expense_list(employee_id=params["employee_id"], auth_token=user_context.token)
                exec_resp = ERPExecutionResponse(
                    success=True,
                    action_type="expense.get_list",
                    message=f"Retrieved {len(expenses)} expense claims.",
                    data={"expenses": expenses}
                )
            elif act_type == ActionType.EXPENSE_APPROVE:
                exec_resp = client.approve_expense_claim(
                    expense_id=params["expense_id"],
                    approver_id=params["approver_id"],
                    decision=params["decision"],
                    notes=params.get("notes"),
                    auth_token=user_context.token
                )
            elif act_type == ActionType.HR_GET_PROFILE:
                profile = client.get_profile(employee_id=params["employee_id"], auth_token=user_context.token)
                exec_resp = ERPExecutionResponse(
                    success=True,
                    action_type="hr.get_profile",
                    message="Employee profile retrieved.",
                    data={"profile": profile}
                )
            elif act_type == ActionType.HR_GET_DIRECTORY:
                directory = client.search_directory(
                    query=params.get("query"),
                    department=params.get("department"),
                    auth_token=user_context.token
                )
                exec_resp = ERPExecutionResponse(
                    success=True,
                    action_type="hr.get_directory",
                    message=f"Found {len(directory)} employee(s) in directory.",
                    data={"directory": directory}
                )
            else:
                return {
                    "status": "ERROR",
                    "final_response": f"Unsupported execution mapping for action type {act_type}"
                }

            if exec_resp.success:
                return {
                    "execution_result": exec_resp,
                    "status": "SUCCESS"
                }
            else:
                return {
                    "execution_result": exec_resp,
                    "status": "ERROR",
                    "final_response": f"ERP Backend Error: {exec_resp.message}"
                }
        except Exception as e:
            return {
                "outage_error": str(e),
                "status": "ERROR",
                "final_response": f"ERP communication failure: Protected action could not be completed ({str(e)})."
            }

def synthesize_final_response(state: ChatState) -> Dict[str, Any]:
    if state.get("final_response"):
        return {}

    clarification = state.get("clarification_message")
    if clarification:
        return {"final_response": clarification}

    val_error = state.get("validation_error")
    if val_error:
        return {"final_response": f"Validation Error: {val_error}"}

    exec_result = state.get("execution_result")
    if exec_result and exec_result.success:
        act_type = exec_result.action_type
        if act_type == "leave.create":
            data = exec_result.data or {}
            resp = (
                f"✅ **Leave Request Created Successfully**\n"
                f"- **Leave ID**: `{data.get('leave_id')}`\n"
                f"- **Dates**: {data.get('start_date')} to {data.get('end_date')}\n"
                f"- **Type**: {data.get('leave_type')}\n"
                f"- **Status**: Pending Manager Approval\n"
                f"- **Backend Confirmation**: {exec_result.message}"
            )
        elif act_type == "expense.submit":
            data = exec_result.data or {}
            resp = (
                f"✅ **Expense Claim Submitted Successfully**\n"
                f"- **Claim ID**: `{data.get('expense_id')}`\n"
                f"- **Amount**: {data.get('currency')} {data.get('amount'):,.2f}\n"
                f"- **Category**: {data.get('category')}\n"
                f"- **Backend Confirmation**: {exec_result.message}"
            )
        elif act_type == "expense.approve":
            data = exec_result.data or {}
            resp = (
                f"✅ **Expense Claim Approved**\n"
                f"- **Claim ID**: `{data.get('expense_id')}`\n"
                f"- **Status**: {data.get('status')}\n"
                f"- **Approver**: `{data.get('approver_id')}`\n"
                f"- **Backend Confirmation**: {exec_result.message}"
            )
        elif act_type == "leave.get_history":
            leaves = (exec_result.data or {}).get("leaves", [])
            resp = f"📋 **Your Leave History ({len(leaves)} record(s))**:\n"
            for l in leaves:
                resp += f"- `{l.get('leave_id')}`: {l.get('leave_type')} ({l.get('start_date')} to {l.get('end_date')}) - **{l.get('status')}**\n"
        elif act_type == "expense.get_list":
            expenses = (exec_result.data or {}).get("expenses", [])
            resp = f"📋 **Your Expense Claims ({len(expenses)} record(s))**:\n"
            for exp in expenses:
                resp += f"- `{exp.get('expense_id')}`: {exp.get('currency')} {exp.get('amount'):,.2f} ({exp.get('category')}) - **{exp.get('status')}**\n"
        elif act_type == "hr.get_profile":
            p = (exec_result.data or {}).get("profile", {})
            resp = (
                f"👤 **Employee Profile**:\n"
                f"- **Name**: {p.get('name')}\n"
                f"- **ID**: `{p.get('employee_id')}`\n"
                f"- **Department**: {p.get('department')}\n"
                f"- **Role**: {p.get('role')}\n"
                f"- **Email**: {p.get('email')}"
            )
        elif act_type == "hr.get_directory":
            directory = (exec_result.data or {}).get("directory", [])
            resp = f"👥 **Company Directory ({len(directory)} result(s))**:\n"
            for d in directory:
                resp += f"- **{d.get('name')}** (`{d.get('employee_id')}`) - {d.get('designation')} ({d.get('department')})\n"
        else:
            resp = f"Operation completed: {exec_result.message}"

        return {"final_response": resp}

    return {"final_response": "Unable to complete request. Please try again."}
