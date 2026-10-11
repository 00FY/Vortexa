"""Domain types and schemas for ActionGate Attacker Side & Gateway Contract."""

from __future__ import annotations
from dataclasses import dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Tuple
import copy
import hashlib
import json
import time
import uuid


class Verdict(str, Enum):
    ALLOW = "ALLOW"
    HOLD = "HOLD"
    BLOCK = "BLOCK"


class Status(str, Enum):
    PENDING = "PENDING"
    ALLOWED = "ALLOWED"
    HELD = "HELD"
    BLOCKED = "BLOCKED"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"
    INVALIDATED = "INVALIDATED"


class DecisionPath(str, Enum):
    RULES_ONLY = "rules_only"
    AI_AGREED = "ai_agreed"
    AI_ESCALATED = "ai_escalated"
    AI_UNAVAILABLE = "ai_unavailable"
    AI_INVALID = "ai_invalid"


class ErrorCode(str, Enum):
    ERR_UNKNOWN_AGENT = "ERR_UNKNOWN_AGENT"
    ERR_UNKNOWN_ACTION = "ERR_UNKNOWN_ACTION"
    ERR_SELF_APPROVAL = "ERR_SELF_APPROVAL"
    ERR_HASH_MISMATCH = "ERR_HASH_MISMATCH"
    ERR_BLOCKED_BY_POLICY = "ERR_BLOCKED_BY_POLICY"
    ERR_ACTION_NOT_PENDING = "ERR_ACTION_NOT_PENDING"
    ERR_REPLAY = "ERR_REPLAY"
    ERR_UNAUTHORIZED_APPROVER = "ERR_UNAUTHORIZED_APPROVER"
    ERR_UNTRUSTED_ARGUMENT_ORIGIN = "ERR_UNTRUSTED_ARGUMENT_ORIGIN"
    ERR_TASK_SCOPE_VIOLATION = "ERR_TASK_SCOPE_VIOLATION"
    ERR_DUPLICATE_ACTION_ID = "ERR_DUPLICATE_ACTION_ID"
    ERR_NOT_APPROVER = "ERR_NOT_APPROVER"
    ERR_UNAUTHENTICATED = "ERR_UNAUTHENTICATED"
    ERR_TASK_NOT_FOUND = "ERR_TASK_NOT_FOUND"


class AuditEvent(str, Enum):
    ACTION_ALLOWED = "action.allowed"
    ACTION_HELD = "action.held"
    ACTION_BLOCKED = "action.blocked"
    ACTION_APPROVED = "action.approved"
    ACTION_EXECUTED = "action.executed"
    ACTION_REJECTED = "action.rejected"
    REFUSAL_LOGGED = "refusal.logged"
    AUDIT_TAMPER_DETECTED = "audit.tamper_detected"
    APPROVAL_INVALIDATED = "approval.invalidated"


class PrincipalType(str, Enum):
    HUMAN_USER = "human_user"
    AGENT = "agent"


@dataclass(frozen=True)
class Principal:
    principal_id: str
    principal_type: PrincipalType
    role: str
    token: str = ""

    def is_human_approver(self) -> bool:
        return self.principal_type == PrincipalType.HUMAN_USER


@dataclass(frozen=True)
class ContextSource:
    source_type: str
    source_id: str
    content: str
    trusted: bool = False


@dataclass(frozen=True)
class ActionRequest:
    agent_id: str
    action_type: str
    arguments: Mapping[str, Any]
    requested_by: str
    context_sources: Tuple[ContextSource, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Deep-copy dictionary and wrap in MappingProxyType for immutability
        raw_args = copy.deepcopy(dict(self.arguments))
        object.__setattr__(self, "arguments", MappingProxyType(raw_args))
        if not isinstance(self.context_sources, tuple):
            object.__setattr__(self, "context_sources", tuple(self.context_sources))
        if not isinstance(self.metadata, MappingProxyType):
            raw_meta = copy.deepcopy(dict(self.metadata))
            object.__setattr__(self, "metadata", MappingProxyType(raw_meta))

    def with_arguments(self, **changes: Any) -> ActionRequest:
        new_args = dict(self.arguments)
        new_args.update(changes)
        return replace(self, arguments=new_args)

    def payload_hash(self) -> str:
        """Deterministic SHA-256 hash strictly over functional payload fields (independent of action_id or timestamp)."""
        normalized = {
            "agent_id": self.agent_id,
            "action_type": self.action_type,
            "arguments": dict(self.arguments),
            "requested_by": self.requested_by,
        }
        encoded = json.dumps(normalized, sort_keys=True, separators=(',', ':')).encode('utf-8')
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    task_type: str
    resource_scope: str
    allowed_operations: Tuple[str, ...]
    assigned_agent: str
    created_by: str = "orchestrator"
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        if not isinstance(self.allowed_operations, tuple):
            object.__setattr__(self, "allowed_operations", tuple(self.allowed_operations))


@dataclass
class Decision:
    action_id: str
    verdict: Verdict
    rule_id: str
    decision_path: DecisionPath
    error_code: Optional[ErrorCode] = None
    reason: str = ""
    ai_recommendation: Optional[Verdict] = None
    action_hash: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class ApprovalRecord:
    action_id: str
    approved_by: str
    action_hash: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class ExecutionResult:
    action_id: str
    success: bool
    verdict: Verdict
    message: str
    state_delta: Dict[str, Any] = field(default_factory=dict)
    error_code: Optional[ErrorCode] = None


@dataclass
class AuditEntry:
    entry_id: str
    event_name: AuditEvent
    action_id: str
    details: Dict[str, Any]
    prev_hash: str
    timestamp: float = field(default_factory=time.time)
    entry_hash: str = ""

    def compute_hash(self) -> str:
        data = {
            "entry_id": self.entry_id,
            "event_name": self.event_name.value if isinstance(self.event_name, AuditEvent) else str(self.event_name),
            "action_id": self.action_id,
            "details": self.details,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
        }
        encoded = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')
        return hashlib.sha256(encoded).hexdigest()


@dataclass
class AttackResult:
    test_id: str
    name: str
    tier: str  # "A" or "B"
    expected_verdict: Verdict
    actual_verdict: Verdict
    expected_error_code: Optional[ErrorCode]
    actual_error_code: Optional[ErrorCode]
    expected_rule_id: str
    actual_rule_id: str
    erp_state_changed: bool
    passed: bool
    details: str
    duration_ms: float = 0.0
