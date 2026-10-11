"""Abstract Gateway Contract that all implementations adhere to."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Optional
from src.types import (
    ActionRequest,
    Decision,
    ExecutionResult,
    AuditEntry,
    Status,
    Principal,
    Verdict,
)


class GatewayContract(ABC):
    @abstractmethod
    def evaluate(self, action: ActionRequest, task_id: str) -> Decision:
        """Evaluate an action against deterministic policy rules, loading task from trusted store."""
        pass

    @abstractmethod
    def approve(self, action_id: str, approver: Principal, action_hash: str) -> Decision:
        """Submit an approval for a held action bound to the exact payload hash."""
        pass

    @abstractmethod
    def execute(self, action_id: str, action: ActionRequest) -> ExecutionResult:
        """Execute an action by verifying the re-hashed payload against approved hash."""
        pass

    @abstractmethod
    def status(self, action_id: str) -> Status:
        """Query current lifecycle status of an action."""
        pass

    @abstractmethod
    def get_audit_log(self) -> List[AuditEntry]:
        """Retrieve the immutable hash-chained audit log."""
        pass

    # Test-only hooks (stripped from demo/production builds)
    def _injectAIResponse(self, response: Optional[Verdict]) -> None:
        pass

    def _corruptAuditRow(self, index: int, field: str, value: Any) -> None:
        pass

    def _resetState(self) -> None:
        pass
