"""AI Advisor Component: Can only escalate or sustain strictness, never relax rules."""

from __future__ import annotations
from typing import Optional
from src.types import ActionRequest, Verdict


class AIUnavailableError(Exception):
    """Raised when the AI advisory service is unavailable/offline."""
    pass


class AIAdvisor:
    def __init__(self, mode: str = "normal"):
        self.mode = mode  # "normal", "offline", "adversarial_allow_all", "escalate_all"
        self._override_response: Optional[Verdict] = None

    def set_override(self, response: Optional[Verdict]) -> None:
        self._override_response = response

    def evaluate_risk(self, action: ActionRequest) -> Verdict:
        if self._override_response is not None:
            return self._override_response

        if self.mode == "offline":
            raise AIUnavailableError("AI Advisor service is currently unreachable.")

        if self.mode == "adversarial_allow_all":
            # Attacker's dream: compromised or jailbroken AI saying ALLOW to everything
            return Verdict.ALLOW

        if self.mode == "escalate_all":
            return Verdict.BLOCK

        # The AI advisor analyzes whether the proposed action's arguments or intent were compromised
        # by looking at suspicious command phrases specifically inside arguments or if the action was hijacked.
        arg_text = str(action.arguments).lower()
        for kw in ["grant admin", "exfiltrate", "evil", "attacker", "delete_database"]:
            if kw in arg_text:
                return Verdict.BLOCK

        return Verdict.ALLOW

