"""Mutant 3: Gate that skips hash-binding check during execution."""

from src.reference_gateway import ReferenceGateway
from src.types import ExecutionResult, Verdict, ActionRequest, Status


class MutantSkipHashCheck(ReferenceGateway):
    def execute(self, action_id: str, action: ActionRequest) -> ExecutionResult:
        # Flaw: Skips hash re-computation and comparison! Executes tampered payload directly!
        if action.action_type == "process_payment":
            amount = float(action.arguments.get("amount", 0))
            self.erp.accounts["ops_account"] -= amount
        self.statuses[action_id] = Status.EXECUTED
        return ExecutionResult(action_id, True, Verdict.ALLOW, "Executed without hash check")
