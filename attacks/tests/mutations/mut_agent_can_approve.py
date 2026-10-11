"""Mutant 11: Gate allowing an agent principal to approve held actions."""

from src.reference_gateway import ReferenceGateway
from src.types import Decision, Verdict, Principal, Status, DecisionPath, ApprovalRecord


class MutantAgentCanApprove(ReferenceGateway):
    def approve(self, action_id: str, approver: Principal, action_hash: str) -> Decision:
        # Flaw: Does not check approver.principal_type; agents can approve!
        action = self.actions[action_id]
        if action.payload_hash() == action_hash:
            self.approvals[action_id] = ApprovalRecord(action_id, approver.principal_id, action_hash)
            self.statuses[action_id] = Status.APPROVED
            dec = Decision(
                action_id=action_id,
                verdict=Verdict.ALLOW,
                rule_id="RULE_MUTANT_AGENT_APPROVED",
                decision_path=DecisionPath.RULES_ONLY,
                action_hash=action_hash,
            )
            self.decisions[action_id] = dec
            return dec
        return super().approve(action_id, approver, action_hash)
