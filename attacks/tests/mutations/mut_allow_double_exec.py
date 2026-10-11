"""Mutant 6: Gate allowing replay / double execution."""

from src.reference_gateway import ReferenceGateway
from src.types import ExecutionResult, Verdict, ActionRequest


class MutantAllowDoubleExec(ReferenceGateway):
    def execute(self, action_id: str, action: ActionRequest) -> ExecutionResult:
        # Flaw: Ignores executed_actions and Status.EXECUTED check! Replays debit repeatedly!
        if action.action_type == "process_payment":
            amount = float(action.arguments.get("amount", 0))
            self.erp.accounts["ops_account"] -= amount
        return ExecutionResult(action_id, True, Verdict.ALLOW, "Replay executed without restriction")
