"""Mutant 8: Gate that trusts agent context_sources unconditionally."""

from src.reference_gateway import ReferenceGateway
from src.types import ActionRequest, Decision, Verdict, DecisionPath, Status


class MutantTrustAgentProvenance(ReferenceGateway):
    def evaluate(self, action: ActionRequest, task_id: str) -> Decision:
        dec = super().evaluate(action, task_id)
        # Flaw: Ignores argument origin verification
        if dec.rule_id == "RULE_ARG_ORIGIN":
            dec.verdict = Verdict.ALLOW
            dec.rule_id = "RULE_MUTANT_TRUST_PROVENANCE"
            dec.error_code = None
            self.decisions[dec.action_id] = dec
            self.statuses[dec.action_id] = Status.ALLOWED
        return dec
