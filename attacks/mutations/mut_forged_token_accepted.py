"""Mutant 12: Gate accepting forged approver authentication tokens."""

from src.reference_gateway import ReferenceGateway
from src.types import Decision, Principal


class MutantForgedTokenAccepted(ReferenceGateway):
    def approve(self, action_id: str, approver: Principal, action_hash: str) -> Decision:
        # Flaw: Completely skips approver token verification!
        # Replaces token with known valid token so check passes
        tampered_principal = Principal(approver.principal_id, approver.principal_type, approver.role, "TOK-KARAN-SECRET")
        return super().approve(action_id, tampered_principal, action_hash)
