"""Mutant 7: Gate that ignores TaskRecord boundaries."""

from src.reference_gateway import ReferenceGateway
from src.types import ActionRequest, Decision, Verdict, DecisionPath, Status


class MutantIgnoreTaskScope(ReferenceGateway):
    def evaluate(self, action: ActionRequest, task_id: str) -> Decision:
        dec = super().evaluate(action, task_id)
        # Flaw: Ignores task.allowed_operations check!
        if dec.rule_id == "RULE_TASK_SCOPE":
            dec.verdict = Verdict.ALLOW
            dec.rule_id = "RULE_MUTANT_NO_TASK_SCOPE"
            dec.error_code = None
            self.decisions[dec.action_id] = dec
            self.statuses[dec.action_id] = Status.ALLOWED
        return dec
