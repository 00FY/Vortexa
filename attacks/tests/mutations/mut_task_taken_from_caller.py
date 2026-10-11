"""Mutant 13: Gate trusting caller-supplied task instead of server-side store."""

from src.reference_gateway import ReferenceGateway
from src.types import ActionRequest, Decision, TaskRecord


class MutantTaskTakenFromCaller(ReferenceGateway):
    def evaluate(self, action: ActionRequest, task_id: str) -> Decision:
        # Flaw: If task_id is unknown, synthesizes an unconstrained permissive task rather than failing!
        if task_id not in self.tasks:
            self.tasks[task_id] = TaskRecord(
                task_id=task_id,
                task_type="forged_permissive",
                resource_scope="all",
                allowed_operations=(action.action_type,),
                assigned_agent=action.agent_id,
            )
        return super().evaluate(action, task_id)
