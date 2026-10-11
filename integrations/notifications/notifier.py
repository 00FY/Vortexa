"""
integrations/notifications/notifier.py
--------------------------------------
Multi-channel notification dispatcher for ActionGate events.
Alerts human approvers when high-value actions enter the HOLD state.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class NotificationEvent(BaseModel):
    decision_id: str
    action_type: str
    target_resource: str
    requester_id: str
    risk_score: float
    action_fingerprint: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class NotificationDispatcher:
    """
    Dispatches approval request notifications across enterprise channels
    (In-app banner, Slack/Webhook, Email).
    """
    def __init__(self):
        self.sent_notifications: List[Dict[str, Any]] = []

    def dispatch_hold_alert(
        self,
        event: NotificationEvent,
        recipient_role: str = "MANAGER"
    ) -> Dict[str, Any]:
        alert = {
            "channel": "ERP_IN_APP_BANNER",
            "decision_id": event.decision_id,
            "target": event.target_resource,
            "risk_score": event.risk_score,
            "action_fingerprint": event.action_fingerprint,
            "headline": f"ActionGate Authorization Required: {event.action_type}",
            "review_url": f"/erp/approvals/{event.target_resource}",
            "dispatched_at": datetime.utcnow().isoformat(),
        }
        self.sent_notifications.append(alert)
        return alert

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self.sent_notifications)
