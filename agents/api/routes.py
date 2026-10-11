import uuid
import time
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Header
from pydantic import BaseModel, Field
from agents.schemas.erp import ERPUserContext, ERPUserRole
from agents.graph.workflow import create_orchestrator_graph
from agents.graph.state import ChatState
from agents.gate_client.actiongate_client import ActionGateClient
from agents.gate_client.erp_client import ERPClient

router = APIRouter()

IDEMPOTENCY_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 300

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User natural language input")
    session_id: Optional[str] = Field(None, description="Chat session ID for context continuity")
    request_id: Optional[str] = Field(None, description="Client-generated unique idempotency token")
    user_context: Optional[ERPUserContext] = Field(
        None,
        description="Verified user context passed from ERP backend session middleware"
    )
    conversation_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Slot states and previous turn metadata"
    )

class ChatResponse(BaseModel):
    request_id: str
    session_id: str
    status: str
    response: str
    decision: Optional[str] = None
    decision_id: Optional[str] = None
    risk_score: Optional[float] = None
    action_type: Optional[str] = None
    action_fingerprint: Optional[str] = None
    missing_fields: Optional[List[str]] = None

default_actiongate_client = ActionGateClient()
default_erp_client = ERPClient()
orchestrator = create_orchestrator_graph(
    actiongate_client=default_actiongate_client,
    erp_client=default_erp_client
)

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "actiongate-ai-agents",
        "timestamp": time.time()
    }

@router.post("/chat", response_model=ChatResponse)
def handle_chat_message(
    payload: ChatRequest,
    authorization: Optional[str] = Header(None)
):
    req_id = payload.request_id or f"REQ-{uuid.uuid4().hex[:8].upper()}"
    now = time.time()
    
    if req_id in IDEMPOTENCY_CACHE:
        cached = IDEMPOTENCY_CACHE[req_id]
        if now - cached["timestamp"] < CACHE_TTL:
            return cached["response"]

    user_ctx = payload.user_context
    if not user_ctx:
        user_ctx = ERPUserContext(
            employee_id="EMP-001",
            name="Rahul Sharma",
            email="rahul.sharma@corp.mini-erp.com",
            role=ERPUserRole.EMPLOYEE,
            department="Engineering",
            manager_id="MGR-002",
            token=authorization.replace("Bearer ", "") if authorization else "test-token"
        )

    sess_id = payload.session_id or f"SESS-{uuid.uuid4().hex[:8].upper()}"

    initial_state: ChatState = {
        "request_id": req_id,
        "session_id": sess_id,
        "user_message": payload.message,
        "user_context": user_ctx,
        "conversation_context": payload.conversation_context or {},
    }

    output_state = orchestrator.invoke(initial_state)

    decision_obj = output_state.get("actiongate_decision")
    action_obj = output_state.get("proposed_action")

    resp = ChatResponse(
        request_id=req_id,
        session_id=sess_id,
        status=output_state.get("status", "SUCCESS"),
        response=output_state.get("final_response", ""),
        decision=decision_obj.decision.value if decision_obj else None,
        decision_id=decision_obj.decision_id if decision_obj else None,
        risk_score=decision_obj.risk_score if decision_obj else None,
        action_type=action_obj.action_type.value if action_obj else None,
        action_fingerprint=action_obj.action_fingerprint if action_obj else None,
        missing_fields=output_state.get("missing_fields"),
    )

    IDEMPOTENCY_CACHE[req_id] = {
        "timestamp": now,
        "response": resp,
    }

    return resp
