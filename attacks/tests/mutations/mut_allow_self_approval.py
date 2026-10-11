"""Mutant 2: Gate that allows requesters to self-approve."""

from src.reference_gateway import ReferenceGateway
from src.types import Decision, Verdict, ApprovalRecord, Principal, Status, DecisionPath


class MutantAllowSelfApproval(ReferenceGateway):
    def approve(self, action_id: str, approver: Principal, action_hash: str) -> Decision:
        # Flaw: Ignores self-approval check!
        action = self.actions[action_id]
        approval = ApprovalRecord(action_id, approver.principal_id, action_hash)
        self.approvals[action_id] = approval
        self.statuses[action_id] = Status.APPROVED
        dec = Decision(
            action_id=action_id,
            verdict=Verdict.ALLOW,
            rule_id="RULE_MUTANT_ALLOW_SELF",
            decision_path=DecisionPath.RULES_ONLY,
            action_hash=action_hash,
        )
        self.decisions[action_id] = dec
        return dec
