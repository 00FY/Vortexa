import re
from typing import Dict, Any, Optional, Tuple, List
from agents.schemas.erp import ERPUserContext
from agents.schemas.actions import ActionType, ProposedAction
from agents.llm.provider import parse_relative_date

class LeaveAgent:
    """
    Specialized agent for Leave management operations.
    Enforces conversational clarification for missing fields instead of guessing.
    Binds the requester employee_id exclusively from verified ERP context.
    """
    def process(
        self,
        user_message: str,
        user_context: ERPUserContext,
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[ProposedAction], Optional[str], Optional[List[str]]]:
        msg = user_message.strip()
        msg_lower = msg.lower()

        # Operation 1: Retrieve Leave History
        if any(kw in msg_lower for kw in ["history", "my leaves", "past leaves", "check balance", "view leaves"]):
            action = ProposedAction.create_and_sign(
                action_type=ActionType.LEAVE_GET_HISTORY,
                target_resource=f"leave:history:{user_context.employee_id}",
                parameters={"employee_id": user_context.employee_id},
                requester_id=user_context.employee_id,
                description=f"Retrieve leave history for employee {user_context.employee_id}"
            )
            return action, None, None

        # Operation 2: Apply for Leave
        prev_slots = conversation_context.get("slots", {}) if conversation_context else {}
        
        # Extract start_date
        start_date = prev_slots.get("start_date")
        extracted_date = parse_relative_date(msg)
        if extracted_date:
            start_date = extracted_date

        # Extract end_date
        end_date = prev_slots.get("end_date") or start_date

        # Extract leave_type
        leave_type = prev_slots.get("leave_type")
        for lt in ["ANNUAL", "SICK", "CASUAL", "MATERNITY", "PATERNITY", "UNPAID"]:
            if lt.lower() in msg_lower:
                leave_type = lt
                break

        # Extract reason
        reason = prev_slots.get("reason")
        reason_match = re.search(r"(?:due to|reason[:\s]+)\s+([a-zA-Z0-9\s,.-]+)", msg, re.IGNORECASE)
        if not reason_match:
            for_match = re.search(r"\bfor\s+(?!leave\b)([a-zA-Z0-9\s,.-]+)", msg, re.IGNORECASE)
            if for_match:
                reason_match = for_match

        if reason_match:
            candidate_reason = reason_match.group(1).strip()
            ignored = {"next monday", "tomorrow", "today", "annual leave", "sick leave", "casual leave", "leave"}
            if candidate_reason.lower() not in ignored and not candidate_reason.lower().startswith("leave "):
                reason = candidate_reason

        # Validate required fields
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
                f"I've noted your request" + (f" for {start_date}" if start_date else "") +
                ". Before I can prepare the leave application for authorization, please provide:\n" +
                "\n".join(prompts)
            )
            return None, clarification, missing_fields

        # All required fields present
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
            requester_id=user_context.employee_id,
            description=f"Create {leave_type} leave request from {start_date} to {end_date} for '{reason}'"
        )
        return action, None, None
