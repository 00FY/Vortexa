"""
agents/specialists/leave_agent.py
----------------------------------
Specialist agent for Leave management operations.

Field extraction strategy
-------------------------
OpenAI mode (LLM_PROVIDER=openai):
    Calls llm_provider.extract_leave_fields() which uses structured output
    (function calling) to extract start_date, end_date, leave_type, reason.
    Results are merged with any previously collected slot values.

Mock mode (LLM_PROVIDER=mock, default):
    Falls back to deterministic regex / keyword logic only — zero API cost.
    All 22 unit tests use this path.

Security invariants
-------------------
- requester employee_id is always taken from the verified ERP session context.
  It is never derived from the user message or LLM output.
- Missing required fields trigger a conversational clarification prompt;
  the agent never guesses or fabricates field values.
- LLMUnavailableError propagates to the node layer for fail-closed handling.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple, List

from agents.schemas.erp import ERPUserContext
from agents.schemas.actions import ActionType, ProposedAction
from agents.llm.provider import parse_relative_date

logger = logging.getLogger(__name__)

_VALID_LEAVE_TYPES = {"ANNUAL", "SICK", "CASUAL", "MATERNITY", "PATERNITY", "UNPAID"}


class LeaveAgent:
    """
    Specialized agent for Leave management.
    Supports leave-history retrieval and new leave-request creation.
    """

    def process(
        self,
        user_message: str,
        user_context: ERPUserContext,
        conversation_context: Optional[Dict[str, Any]] = None,
        llm_provider=None,
    ) -> Tuple[Optional[ProposedAction], Optional[str], Optional[List[str]]]:
        """
        Process a leave-related user message.

        Parameters
        ----------
        user_message         : Raw message text from the chatbot.
        user_context         : Verified ERP session identity (never from message).
        conversation_context : Slot state from previous turns.
        llm_provider         : LLMProvider instance (injected from graph node).
                               If None, regex-only mode is used.

        Returns
        -------
        (ProposedAction, None, None)           — ready to submit to ActionGate
        (None, clarification_str, [fields])    — ask user for missing info
        """
        msg = user_message.strip()
        msg_lower = msg.lower()

        # ---------------------------------------------------------------
        # Operation 1: Retrieve Leave History  (no LLM needed)
        # ---------------------------------------------------------------
        if any(kw in msg_lower for kw in [
            "history", "my leaves", "past leaves", "check balance", "view leaves"
        ]):
            action = ProposedAction.create_and_sign(
                action_type=ActionType.LEAVE_GET_HISTORY,
                target_resource=f"leave:history:{user_context.employee_id}",
                parameters={"employee_id": user_context.employee_id},
                requester_id=user_context.employee_id,
                description=f"Retrieve leave history for employee {user_context.employee_id}",
            )
            return action, None, None

        # ---------------------------------------------------------------
        # Operation 2: Apply for Leave
        # ---------------------------------------------------------------
        prev_slots = conversation_context.get("slots", {}) if conversation_context else {}

        # --- LLM extraction (when available) ---
        llm_fields: Dict[str, Any] = {}
        if llm_provider is not None:
            # Will raise LLMUnavailableError if OpenAI configured but down —
            # that propagates to the node for fail-closed handling.
            llm_fields = llm_provider.extract_leave_fields(msg, conversation_context or {})
            if llm_fields:
                logger.debug("Leave fields from LLM: %s", llm_fields)

        # --- Merge: LLM > regex > prev_slots (lowest priority) ---

        # start_date
        start_date = llm_fields.get("start_date") or prev_slots.get("start_date")
        if not start_date:
            start_date = parse_relative_date(msg)

        # end_date
        end_date = (
            llm_fields.get("end_date")
            or prev_slots.get("end_date")
            or start_date  # default to single-day leave
        )

        # leave_type
        leave_type = llm_fields.get("leave_type") or prev_slots.get("leave_type")
        if not leave_type:
            # Regex keyword fallback
            for lt in _VALID_LEAVE_TYPES:
                if lt.lower() in msg_lower:
                    leave_type = lt
                    break

        # reason
        reason = llm_fields.get("reason") or prev_slots.get("reason")
        if not reason:
            # Regex patterns
            reason_match = re.search(
                r"(?:due to|reason[:\s]+)\s+([a-zA-Z0-9\s,.-]+)", msg, re.IGNORECASE
            )
            if not reason_match:
                for_match = re.search(
                    r"\bfor\s+(?!leave\b)([a-zA-Z0-9\s,.-]+)", msg, re.IGNORECASE
                )
                if for_match:
                    reason_match = for_match
            if reason_match:
                candidate = reason_match.group(1).strip()
                ignored = {
                    "next monday", "tomorrow", "today",
                    "annual leave", "sick leave", "casual leave", "leave",
                }
                if candidate.lower() not in ignored and not candidate.lower().startswith("leave "):
                    reason = candidate

        # --- Validate required fields ---
        missing_fields: List[str] = []
        if not start_date:
            missing_fields.append("start_date")
        if not leave_type:
            missing_fields.append("leave_type")
        if not reason:
            missing_fields.append("reason")

        if missing_fields:
            prompts = []
            if "start_date" in missing_fields:
                prompts.append("• The date(s) of your intended leave")
            if "leave_type" in missing_fields:
                prompts.append("• The type of leave (e.g. ANNUAL, SICK, CASUAL)")
            if "reason" in missing_fields:
                prompts.append("• A brief reason for the leave")

            clarification = (
                "I've noted your request"
                + (f" for {start_date}" if start_date else "")
                + ". Before I can prepare the leave application for authorization, please provide:\n"
                + "\n".join(prompts)
            )
            return None, clarification, missing_fields

        # All required fields present — build signed proposal
        action = ProposedAction.create_and_sign(
            action_type=ActionType.LEAVE_CREATE,
            target_resource="erp:leave_request",
            parameters={
                "employee_id": user_context.employee_id,
                "leave_type": leave_type,
                "start_date": start_date,
                "end_date": end_date,
                "reason": reason,
            },
            requester_id=user_context.employee_id,  # Always from auth context
            description=(
                f"Create {leave_type} leave request from {start_date} to {end_date} "
                f"for '{reason}'"
            ),
        )
        return action, None, None
