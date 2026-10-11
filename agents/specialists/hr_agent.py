"""
agents/specialists/hr_agent.py
-------------------------------
Specialist agent for HR operations.

Supports:
  - Employee profile retrieval (always the authenticated user's own profile)
  - Company directory search (by department / free-text query)

Security invariants
-------------------
- Profile lookup always uses user_context.employee_id from the verified ERP
  session. The message content and LLM output cannot redirect this to another
  employee's record — enforcing Case H (access violation prevention).
- requester_id is always from auth context.
- The llm_provider parameter is accepted for interface consistency but is not
  required for HR operations (keyword matching is unambiguous here).
"""

import logging
from typing import Dict, Any, Optional, Tuple

from agents.schemas.erp import ERPUserContext
from agents.schemas.actions import ActionType, ProposedAction

logger = logging.getLogger(__name__)


class HRAgent:
    """
    Specialized agent for HR operations.
    Supports verified employee profile retrieval and directory searches.
    """

    def process(
        self,
        user_message: str,
        user_context: ERPUserContext,
        conversation_context: Optional[Dict[str, Any]] = None,
        llm_provider=None,
    ) -> Tuple[Optional[ProposedAction], Optional[str], Optional[list]]:
        """
        Process an HR-related user message.

        Parameters
        ----------
        user_message  : Raw message text from the chatbot.
        user_context  : Verified ERP session identity.
        llm_provider  : Accepted for interface consistency; HR ops use
                        keyword matching which is unambiguous.

        Returns
        -------
        (ProposedAction, None, None) — always ready (HR ops have no missing fields)
        """
        msg = user_message.lower()

        # ---------------------------------------------------------------
        # Case 1: Directory search
        # ---------------------------------------------------------------
        if any(kw in msg for kw in [
            "directory", "search employee", "find colleague", "who works in"
        ]):
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
                description=f"Directory lookup for department {dept or 'all'}",
            )
            return action, None, None

        # ---------------------------------------------------------------
        # Case 2: Profile lookup
        # Security: ALWAYS uses the authenticated user's employee_id.
        # Even if the message names another employee, the ERP access-control
        # layer enforces that a user can only read their own profile via
        # this action type.  Cross-user access is Case H.
        # ---------------------------------------------------------------
        action = ProposedAction.create_and_sign(
            action_type=ActionType.HR_GET_PROFILE,
            target_resource=f"employee:{user_context.employee_id}",
            parameters={"employee_id": user_context.employee_id},
            requester_id=user_context.employee_id,
            description=(
                f"Fetch profile details for verified employee {user_context.employee_id}"
            ),
        )
        return action, None, None
