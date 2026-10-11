"""FastAPI HTTP Adapter providing REST interface to ActionGate for integration and Attack Lab UI."""

from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import time

from src.reference_gateway import ReferenceGateway
from src.types import (
    ActionRequest,
    ContextSource,
    Verdict,
    ErrorCode,
    Principal,
    PrincipalType,
)
from runner.attack_runner import AttackRunner
from runner.interpreter import FreeformInterpreter, REGISTERED_TASKS

app = FastAPI(title="ActionGate Attack Lab API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gateway = ReferenceGateway()
interpreter = FreeformInterpreter()


class ContextSourceModel(BaseModel):
    source_type: str
    source_id: str
    content: str
    trusted: bool = False


class ActionRequestModel(BaseModel):
    action_type: str
    arguments: Dict[str, Any]
    requested_by: str
    agent_id: str
    context_sources: List[ContextSourceModel] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvaluatePayload(BaseModel):
    action: ActionRequestModel
    task_id: str


class ApprovePayload(BaseModel):
    approver_id: str
    token: str
    role: str = "kyc_officer"
    action_hash: str


class ExecutePayload(BaseModel):
    action: ActionRequestModel


class FreeformAttackPayload(BaseModel):
    prompt: str
    task_id: str
    user_role: str = "riya"
    session_id: str = "default_session"


@app.get("/health")
def health():
    return {"status": "ok", "service": "ActionGate Reference Gateway", "version": "1.1.0"}


@app.get("/tasks")
def get_tasks():
    return list(REGISTERED_TASKS.values())


@app.get("/report")
def get_attack_report():
    runner = AttackRunner()
    return runner.run_all()


@app.post("/evaluate")
def evaluate_action(payload: EvaluatePayload):
    sources = tuple([
        ContextSource(
            source_type=c.source_type,
            source_id=c.source_id,
            content=c.content,
            trusted=c.trusted,
        )
        for c in payload.action.context_sources
    ])
    act = ActionRequest(
        action_type=payload.action.action_type,
        arguments=payload.action.arguments,
        requested_by=payload.action.requested_by,
        agent_id=payload.action.agent_id,
        context_sources=sources,
        metadata=payload.action.metadata,
    )
    decision = gateway.evaluate(act, payload.task_id)
    return {
        "action_id": decision.action_id,
        "verdict": decision.verdict.value,
        "rule_id": decision.rule_id,
        "decision_path": decision.decision_path.value,
        "error_code": decision.error_code.value if decision.error_code else None,
        "reason": decision.reason,
        "ai_recommendation": decision.ai_recommendation.value if decision.ai_recommendation else None,
        "action_hash": decision.action_hash,
    }


@app.post("/approve/{action_id}")
def approve_action(action_id: str, payload: ApprovePayload):
    approver = Principal(
        principal_id=payload.approver_id,
        principal_type=PrincipalType.HUMAN_USER,
        role=payload.role,
        token=payload.token,
    )
    decision = gateway.approve(action_id, approver, payload.action_hash)
    return {
        "action_id": decision.action_id,
        "verdict": decision.verdict.value,
        "rule_id": decision.rule_id,
        "decision_path": decision.decision_path.value,
        "error_code": decision.error_code.value if decision.error_code else None,
        "reason": decision.reason,
    }


@app.post("/execute/{action_id}")
def execute_action(action_id: str, payload: ExecutePayload):
    sources = tuple([
        ContextSource(
            source_type=c.source_type,
            source_id=c.source_id,
            content=c.content,
            trusted=c.trusted,
        )
        for c in payload.action.context_sources
    ])
    act = ActionRequest(
        action_type=payload.action.action_type,
        arguments=payload.action.arguments,
        requested_by=payload.action.requested_by,
        agent_id=payload.action.agent_id,
        context_sources=sources,
        metadata=payload.action.metadata,
    )
    res = gateway.execute(action_id, act)
    return {
        "action_id": res.action_id,
        "success": res.success,
        "verdict": res.verdict.value,
        "message": res.message,
        "error_code": res.error_code.value if res.error_code else None,
        "state_delta": res.state_delta,
    }


@app.get("/status/{action_id}")
def get_status(action_id: str):
    return {"action_id": action_id, "status": gateway.status(action_id).value}


@app.get("/audit")
def get_audit():
    return [
        {
            "entry_id": e.entry_id,
            "event_name": e.event_name.value,
            "action_id": e.action_id,
            "details": e.details,
            "prev_hash": e.prev_hash,
            "entry_hash": e.entry_hash,
            "timestamp": e.timestamp,
        }
        for e in gateway.get_audit_log()
    ]


@app.post("/interpret")
def interpret_freeform(payload: FreeformAttackPayload):
    success, scenario, msg = interpreter.interpret(
        payload.prompt,
        payload.task_id,
        payload.user_role,
        payload.session_id,
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"scenario": scenario, "message": msg}


@app.post("/reset")
def reset_state():
    gateway._resetState()
    return {"message": "ERP State, Tasks, and Audit Log reset to initial pristine state."}
