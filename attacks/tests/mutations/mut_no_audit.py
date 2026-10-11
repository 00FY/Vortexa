"""Mutant 5: Gate that omits audit logging entirely."""

from src.reference_gateway import ReferenceGateway
from src.types import ActionRequest, Decision


class MutantNoAudit(ReferenceGateway):
    def evaluate(self, action: ActionRequest, task_id: str) -> Decision:
        dec = super().evaluate(action, task_id)
        # Flaw: Wipes audit entries
        self.audit_log.entries.clear()
        return dec
