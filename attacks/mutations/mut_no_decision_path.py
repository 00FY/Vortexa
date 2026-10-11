"""Mutant 14: Gate failing to record decision_path in Decision."""

from src.reference_gateway import ReferenceGateway
from src.types import ActionRequest, Decision


class MutantNoDecisionPath(ReferenceGateway):
    def evaluate(self, action: ActionRequest, task_id: str) -> Decision:
        dec = super().evaluate(action, task_id)
        # Flaw: Wipes decision_path back to None or blank
        dec.decision_path = None  # type: ignore
        return dec
