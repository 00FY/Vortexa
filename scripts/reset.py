"""
scripts/reset.py
----------------
Resets ERP database state, clears pending authorization holds, and restores
the ActionGate environment to its pristine initial baseline.
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.gate_client.mocks import MockERP, MockActionGate
from agents.api.routes import IDEMPOTENCY_CACHE

def reset_environment():
    print("=" * 70)
    print("  RESETTING ACTIONGATE & ERP DEMO ENVIRONMENT")
    print("=" * 70)

    erp = MockERP()
    erp.reset()
    print("  ✓ ERP state restored to initial baseline.")

    actiongate = MockActionGate(erp_backend=erp)
    actiongate.reset()
    print("  ✓ ActionGate decision registry, holds, and audit log reset.")

    IDEMPOTENCY_CACHE.clear()
    print("  ✓ API idempotency cache cleared.")

    print("\n" + "=" * 70)
    print("  SYSTEM RESET COMPLETE — ENVIRONMENT PRISTINE.")
    print("=" * 70)

if __name__ == "__main__":
    reset_environment()
