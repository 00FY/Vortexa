"""Mutant 10: Gate where a wrong-hash approval attempt BLOCKS/KILLS the action (DoS flaw)."""

from src.reference_gateway import ReferenceGateway
from src.types import Decision, Verdict, ErrorCode, Principal, Status, DecisionPath


class MutantWrongHashBlocksAction(ReferenceGateway):
    def approve(self, action_id: str, approver: Principal, action_hash: str) -> Decision:
        action = self.actions[action_id]
        if action.payload_hash() != action_hash:
            # Flaw: Wrong hash causes the pending action to transition to BLOCKED!
            self.statuses[action_id] = Status.BLOCKED
            return Decision(
                action_id=action_id,
                verdict=Verdict.BLOCK,
                rule_id="RULE_MUTANT_WRONG_HASH_BLOCKS",
                decision_path=DecisionPath.RULES_ONLY,
                error_code=ErrorCode.ERR_HASH_MISMATCH,
                reason="Wrong hash killed the action",
            )
        return super().approve(action_id, approver, action_hash)
