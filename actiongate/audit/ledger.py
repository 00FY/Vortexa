"""Tamper-evident hash-chained audit ledger for ActionGate."""

from __future__ import annotations
from enum import Enum
from typing import Dict, Any, List, Optional
import time
import json
import hashlib
from pydantic import BaseModel, Field


class AuditEvent(str, Enum):
    DECISION_RECORDED = "decision.recorded"
    APPROVAL_REGISTERED = "approval.registered"
    EXECUTION_ATTEMPTED = "execution.attempted"
    REFUSAL_LOGGED = "refusal.logged"
    APPROVAL_INVALIDATED = "approval.invalidated"
    AUDIT_TAMPER_DETECTED = "audit.tamper_detected"


class AuditEntry(BaseModel):
    entry_id: str
    event_name: AuditEvent
    request_id: str
    details: Dict[str, Any]
    timestamp: float = Field(default_factory=time.time)
    prev_hash: str
    entry_hash: str = ""

    def compute_hash(self) -> str:
        """Computes deterministic SHA-256 hash strictly over functional ledger fields."""
        payload = {
            "prev_hash": self.prev_hash,
            "entry_id": self.entry_id,
            "event_name": self.event_name.value,
            "request_id": self.request_id,
            "details": self.details,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class AuditLedger:
    GENESIS_HASH = "0" * 64

    def __init__(self):
        self.entries: List[AuditEntry] = []

    def log(self, event_name: AuditEvent, request_id: str, details: Dict[str, Any]) -> AuditEntry:
        """Appends an event to the ledger, binding it into the cryptographic hash chain."""
        entry_id = f"AUD-{len(self.entries) + 1:06d}"
        prev_hash = self.entries[-1].entry_hash if self.entries else self.GENESIS_HASH

        entry = AuditEntry(
            entry_id=entry_id,
            event_name=event_name,
            request_id=request_id,
            details=details,
            prev_hash=prev_hash,
        )
        entry.entry_hash = entry.compute_hash()
        self.entries.append(entry)
        return entry

    def get_entries(self) -> List[AuditEntry]:
        return list(self.entries)

    def size(self) -> int:
        return len(self.entries)
