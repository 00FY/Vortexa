"""Mutant 4: Gate where AI advice relaxes strict rules (uses min/least strict)."""

from src.reference_gateway import ReferenceGateway
from src.types import ActionRequest, Decision, Verdict, DecisionPath, Status


class MutantAICanRelax(ReferenceGateway):
    def evaluate(self, action: ActionRequest, task_id: str) -> Decision:
        dec = super().evaluate(action, task_id)
        # Flaw: If AI returns ALLOW, it overrides HOLD or BLOCK!
        ai_verdict = self.ai_advisor.evaluate_risk(action)
        if ai_verdict == Verdict.ALLOW:
            dec.verdict = Verdict.ALLOW
            dec.rule_id = "RULE_MUTANT_AI_RELAX"
            dec.decision_path = DecisionPath.AI_AGREED
            self.decisions[dec.action_id] = dec
            self.statuses[dec.action_id] = Status.ALLOWED
        return dec
