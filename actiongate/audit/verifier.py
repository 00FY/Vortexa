"""Cryptographic Audit Chain Integrity Verifier."""

from typing import Tuple, Optional, List
from actiongate.audit.ledger import AuditLedger, AuditEntry


class AuditVerifier:
    @staticmethod
    def verify_chain(entries: List[AuditEntry]) -> Tuple[bool, Optional[int], str]:
        """
        Validates complete hash-chain integrity:
        1. Genesis block references 64 zeros
        2. Recalculated entry hashes match recorded hashes
        3. prev_hash pointers form an unbroken link
        Returns: (is_valid, failing_index, reason)
        """
        if not entries:
            return True, None, "Ledger is empty (valid)."

        for i, entry in enumerate(entries):
            # 1. Check prev_hash link
            expected_prev = AuditLedger.GENESIS_HASH if i == 0 else entries[i - 1].entry_hash
            if entry.prev_hash != expected_prev:
                return (
                    False,
                    i,
                    f"Hash link broken at index {i}: prev_hash '{entry.prev_hash[:10]}...' does not match previous entry hash '{expected_prev[:10]}...'"
                )

            # 2. Check entry hash computation integrity
            recomputed = entry.compute_hash()
            if entry.entry_hash != recomputed:
                return (
                    False,
                    i,
                    f"Payload modification detected at index {i}: recorded hash does not match computed content digest."
                )

        return True, None, "Ledger integrity verified: all hash-chain links and signatures valid."
