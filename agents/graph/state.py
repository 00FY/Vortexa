from typing import TypedDict, Optional, List, Dict, Any
from agents.schemas.erp import ERPUserContext, ERPExecutionResponse
from agents.schemas.actions import ProposedAction
from agents.schemas.actiongate import ActionGateDecision

class ChatState(TypedDict, total=False):
    request_id: str
    session_id: str
    user_message: str
    user_context: ERPUserContext
    conversation_context: Dict[str, Any]
    
    # Routing & Agent outputs
    intent: Optional[str]
    proposed_action: Optional[ProposedAction]
    missing_fields: Optional[List[str]]
    clarification_message: Optional[str]
    validation_error: Optional[str]
    
    # Security & Evaluation
    actiongate_decision: Optional[ActionGateDecision]
    
    # Execution & Output
    execution_result: Optional[ERPExecutionResponse]
    outage_error: Optional[str]
    final_response: str
    status: str  # "SUCCESS", "BLOCKED", "HELD", "NEEDS_CLARIFICATION", "ERROR"
