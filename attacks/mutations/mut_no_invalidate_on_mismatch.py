"""Mutant 9: Gate where approval is NOT invalidated upon execution hash mismatch."""

from src.reference_gateway import ReferenceGateway
from src.types import ExecutionResult, Verdict, ErrorCode, ActionRequest, Status


class MutantNoInvalidateOnMismatch(ReferenceGateway):
    def execute(self, action_id: str, action: ActionRequest) -> ExecutionResult:
        incoming_hash = action.payload_hash()
        expected_hash = self.decisions[action_id].action_hash
        if action_id in self.approvals:
            expected_hash = self.approvals[action_id].action_hash

        if incoming_hash != expected_hash:
            # Flaw: Refuses execution but does NOT invalidate approval; leaves status APPROVED!
            return ExecutionResult(
                action_id=action_id,
                success=False,
                verdict=Verdict.BLOCK,
                message="Mismatch but approval kept alive",
                error_code=ErrorCode.ERR_HASH_MISMATCH,
            )

        return super().execute(action_id, action)
