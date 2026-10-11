from typing import Dict, Any, Optional, Tuple
from agents.schemas.erp import ERPUserContext
from agents.schemas.actions import ActionType, ProposedAction

class HRAgent:
    """
    Specialized agent for HR operations.
    Supports verified employee profile retrieval and directory searches.
    """
    def process(
        self,
        user_message: str,
        user_context: ERPUserContext,
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[ProposedAction], Optional[str], Optional[list]]:
        msg = user_message.lower()

        # Case 1: Directory search
        if any(kw in msg for kw in ["directory", "search employee", "find colleague", "who works in"]):
            dept = None
            if "engineering" in msg:
                dept = "Engineering"
            elif "sales" in msg:
                dept = "Sales"
            elif "finance" in msg:
                dept = "Finance"
                
            action = ProposedAction.create_and_sign(
                action_type=ActionType.HR_GET_DIRECTORY,
                target_resource="erp:directory",
                parameters={"department": dept, "query": None},
                requester_id=user_context.employee_id,
                description=f"Directory lookup for department {dept or 'all'}"
            )
            return action, None, None

        # Case 2: Employee profile lookup (always for the verified authenticated user)
        action = ProposedAction.create_and_sign(
            action_type=ActionType.HR_GET_PROFILE,
            target_resource=f"employee:{user_context.employee_id}",
            parameters={"employee_id": user_context.employee_id},
            requester_id=user_context.employee_id,
            description=f"Fetch profile details for verified employee {user_context.employee_id}"
        )
        return action, None, None
