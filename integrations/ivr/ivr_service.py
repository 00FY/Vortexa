"""
integrations/ivr/ivr_service.py
-------------------------------
Interactive Voice Response (IVR) phone approval gateway simulation.
Allows managers to formally approve or reject HELD actions out-of-band via phone/telephony.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

class IVRCallSession(BaseModel):
    call_sid: str
    manager_phone: str
    decision_id: str
    action_fingerprint: str
    status: str = "RINGING"  # RINGING, IN_PROGRESS, APPROVED, REJECTED

class IVRApprovalService:
    """
    Simulates automated IVR phone calls to managers for high-value approvals.
    Generates TwiML-compatible voice prompts and registers keypad confirmation.
    """
    def __init__(self):
        self.active_sessions: Dict[str, IVRCallSession] = {}

    def initiate_approval_call(
        self,
        manager_phone: str,
        decision_id: str,
        action_fingerprint: str,
        expense_amount: float
    ) -> IVRCallSession:
        session_id = f"CA-{abs(hash(decision_id)) % 10000000}"
        session = IVRCallSession(
            call_sid=session_id,
            manager_phone=manager_phone,
            decision_id=decision_id,
            action_fingerprint=action_fingerprint,
            status="IN_PROGRESS"
        )
        self.active_sessions[session_id] = session
        return session

    def process_keypad_input(self, call_sid: str, digits: str) -> Dict[str, Any]:
        session = self.active_sessions.get(call_sid)
        if not session:
            return {"status": "ERROR", "message": "Call session expired"}

        if digits == "1":
            session.status = "APPROVED"
            return {
                "status": "APPROVED",
                "decision_id": session.decision_id,
                "action_fingerprint": session.action_fingerprint,
                "message": "Manager pressed 1: Formal authorization recorded."
            }
        elif digits == "2":
            session.status = "REJECTED"
            return {
                "status": "REJECTED",
                "decision_id": session.decision_id,
                "action_fingerprint": session.action_fingerprint,
                "message": "Manager pressed 2: Operation rejected."
            }
        return {"status": "INVALID_INPUT", "message": "Press 1 to approve, 2 to reject."}
