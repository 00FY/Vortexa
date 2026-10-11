"""Action-bound human approval manager with cryptographic fingerprint binding and TTL."""

from typing import Dict, Optional, Tuple
import time
from actiongate.types import (
    ActionGateApprovalSubmission,
    ErrorCode,
)


class ApprovalManager:
    DEFAULT_TTL_SECONDS = 300.0  # 5 minutes expiry window

    def __init__(self, ttl_seconds: float = DEFAULT_TTL_SECONDS):
        self.ttl_seconds = ttl_seconds
        self.registry: Dict[str, ActionGateApprovalSubmission] = {}
        self.consumed_fingerprints: set[str] = set()

    def register_approval(
        self,
        decision_id: str,
        approver_id: str,
        approver_role: str,
        action_fingerprint: str,
        status: str = "APPROVED",
        notes: Optional[str] = None,
    ) -> ActionGateApprovalSubmission:
        """Registers a formal human approval cryptographically bound to the action fingerprint."""
        submission = ActionGateApprovalSubmission(
            decision_id=decision_id,
            approver_id=approver_id,
            approver_role=approver_role,
            action_fingerprint=action_fingerprint,
            status=status.upper(),
            notes=notes,
            timestamp=time.time(),
        )
        self.registry[action_fingerprint] = submission
        return submission

    def validate_approval(
        self,
        action_fingerprint: str,
        required_role: Optional[str] = None,
    ) -> Tuple[bool, Optional[ActionGateApprovalSubmission], Optional[ErrorCode], str]:
        """
        Validates approval:
        1. Exists in registry
        2. Status is APPROVED
        3. Within TTL expiry window
        4. Matches required approver role
        5. Has not been replayed / double-consumed
        """
        if action_fingerprint in self.consumed_fingerprints:
            return False, None, ErrorCode.ERR_REPLAY, "Approval signature has already been consumed (replay prevention)."

        submission = self.registry.get(action_fingerprint)
        if not submission:
            return False, None, ErrorCode.ERR_ACTION_NOT_PENDING, "No approval record found for the exact action fingerprint."

        if submission.status != "APPROVED":
            return False, submission, ErrorCode.ERR_BLOCKED_BY_POLICY, f"Action approval was formally rejected by {submission.approver_id}."

        # TTL expiry check
        if (time.time() - submission.timestamp) > self.ttl_seconds:
            # Invalidate expired approval
            del self.registry[action_fingerprint]
            return False, None, ErrorCode.ERR_ACTION_NOT_PENDING, "Approval signature has expired (TTL window exceeded)."

        # Role validation
        if required_role and submission.approver_role.upper() != required_role.upper():
            return False, submission, ErrorCode.ERR_UNAUTHORIZED_APPROVER, f"Approver role '{submission.approver_role}' does not satisfy required role '{required_role}'."

        return True, submission, None, "Valid approval record verified."

    def consume(self, action_fingerprint: str) -> None:
        """Marks the approval as executed to prevent replay."""
        self.consumed_fingerprints.add(action_fingerprint)
        if action_fingerprint in self.registry:
            del self.registry[action_fingerprint]
