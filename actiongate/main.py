"""
actiongate/main.py
------------------
FastAPI entrypoint for the ActionGate Authorization Engine (running on port 8001).
Evaluates proposed AI agent actions against deterministic security policies,
calculates WARS risk scores, manages approval workflows, and maintains the audit ledger.
"""

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents.schemas.actiongate import (
    ActionGateRequest,
    ActionGateDecision,
    DecisionType,
    RiskLevel,
    HoldDetails,
    ActionGateApprovalSubmission,
)
from agents.gate_client.mocks import MockActionGate, MockERP

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ActionGate Authorization Engine",
    description="Deterministic AI Agent Action Authorization Gateway · Problem Statement C-01",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Engine State Singleton
_erp = MockERP()
_engine = MockActionGate(erp_backend=_erp)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "actiongate-authorization-engine",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/v1/evaluate", response_model=ActionGateDecision)
def evaluate_action_proposal(
    request: ActionGateRequest,
    authorization: Optional[str] = Header(None),
):
    """
    Evaluates an action proposal against deterministic policies and risk scoring.
    Returns ALLOW, HOLD, or BLOCK.
    """
    try:
        decision = _engine.evaluate(request)
        return decision
    except Exception as e:
        logger.error(f"Policy evaluation failure: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/approve")
def submit_formal_approval(payload: ActionGateApprovalSubmission):
    """
    Registers an out-of-band formal approval (e.g., from ERP Portal or IVR)
    binding the decision to the exact action fingerprint.
    """
    try:
        res = _engine.register_erp_approval(
            decision_id=payload.decision_id,
            approver_id=payload.approver_id,
            approver_role=payload.approver_role,
            action_fingerprint=payload.action_fingerprint,
        )
        return {"status": "SUCCESS", "message": "Approval registered successfully"}
    except Exception as e:
        logger.error(f"Approval submission failure: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/audit")
def get_audit_trail():
    """Returns the cryptographic hash-chained audit ledger."""
    return _engine.audit_log


@app.post("/api/v1/reset")
def reset_engine():
    """Resets policies, holds, and state to pristine baseline."""
    _engine.reset()
    _erp.reset()
    return {"status": "SUCCESS", "message": "ActionGate state reset to baseline."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("actiongate.main:app", host="0.0.0.0", port=8001, reload=True)
