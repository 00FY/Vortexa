"""Mutant 1: Gate that mistakenly allows unknown agents."""

from src.reference_gateway import ReferenceGateway
from src.types import ActionRequest, Decision, Verdict, DecisionPath


class MutantAllowUnknownAgent(ReferenceGateway):
    def evaluate(self, action: ActionRequest, task_id: str) -> Decision:
        # Flaw: Bypasses agent allowlist check entirely
        dec = super().evaluate(action, task_id)
        if action.agent_id not in {"agent-001", "agent-002", "agent-003", "agent-004"}:
            # Mutant forces ALLOW instead of BLOCK
            dec.verdict = Verdict.ALLOW
            dec.rule_id = "RULE_MUTANT_BYPASS_AGENT"
            dec.error_code = None
            self.decisions[dec.action_id] = dec
            self.statuses[dec.action_id] = "ALLOWED"
        return dec
