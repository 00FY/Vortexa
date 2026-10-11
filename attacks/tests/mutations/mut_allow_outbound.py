"""Mutant 15: Gate that permits outbound transmission without blocking."""

from src.reference_gateway import ReferenceGateway
from src.types import ActionRequest, Decision, Verdict, Status


class MutantAllowOutbound(ReferenceGateway):
    def evaluate(self, action: ActionRequest, task_id: str) -> Decision:
        dec = super().evaluate(action, task_id)
        if action.action_type == "send_outbound":
            # Flaw: Permits outbound transmission instead of blocking
            dec.verdict = Verdict.ALLOW
            dec.rule_id = "RULE_MUTANT_ALLOW_OUTBOUND"
            dec.error_code = None
            self.statuses[dec.action_id] = Status.ALLOWED
            self.decisions[dec.action_id] = dec
        return dec
