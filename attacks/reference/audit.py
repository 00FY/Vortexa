"""Hash-Chained Append-Only Tamper-Evident Audit Log."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import uuid
import time
from src.types import AuditEntry, AuditEvent


class AuditLog:
    def __init__(self):
        self.entries: List[AuditEntry] = []
        self._genesis_hash = "0" * 64

    def log(self, event_name: AuditEvent, action_id: str, details: Dict[str, Any]) -> AuditEntry:
        prev_hash = self.entries[-1].entry_hash if self.entries else self._genesis_hash
        entry = AuditEntry(
            entry_id=str(uuid.uuid4()),
            event_name=event_name,
            action_id=action_id,
            details=details,
            prev_hash=prev_hash,
            timestamp=time.time(),
        )
        entry.entry_hash = entry.compute_hash()
        self.entries.append(entry)
        return entry

    def verify_chain(self) -> tuple[bool, Optional[int]]:
        """
        Verify cryptographic integrity of the entire chain.
        Returns (True, None) if intact, or (False, broken_index) if tampering detected.
        """
        expected_prev = self._genesis_hash
        for i, entry in enumerate(self.entries):
            # Check previous link
            if entry.prev_hash != expected_prev:
                return False, i
            # Check internal integrity hash
            if entry.compute_hash() != entry.entry_hash:
                return False, i
            expected_prev = entry.entry_hash
        return True, None

    def corrupt_row(self, index: int, field: str, value: Any) -> None:
        """Test hook: intentionally tamper with an entry without recalculating hash."""
        if 0 <= index < len(self.entries):
            setattr(self.entries[index], field, value)

    def get_entries(self) -> List[AuditEntry]:
        return list(self.entries)
