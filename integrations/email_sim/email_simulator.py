"""
integrations/email_sim/email_simulator.py
-----------------------------------------
Simulates corporate email intake for employee business workflows.
Enforces screening before forwarding email contents to AI Orchestrator.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from integrations.screening import ContentScreener

class SimulatedEmail(BaseModel):
    message_id: str
    sender_email: str
    recipient_email: str
    subject: str
    body: str
    received_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class EmailSimulator:
    def __init__(self, screener: Optional[ContentScreener] = None):
        self.screener = screener or ContentScreener()

    def process_incoming_email(self, email: SimulatedEmail) -> Dict[str, Any]:
        """
        Screens incoming email for injection attacks and forwards safe requests.
        """
        screening = self.screener.screen_text(email.body)
        
        return {
            "message_id": email.message_id,
            "sender": email.sender_email,
            "subject": email.subject,
            "screened_safe": screening.is_safe,
            "risk_flags": screening.risk_flags,
            "content_for_agent": screening.sanitized_content,
        }
