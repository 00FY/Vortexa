"""Property Test P1: Gateway-Integrated Lattice Invariant.

Formal Security Guarantee:
AI advice must NEVER relax deterministic policy rules:
    ∀ action, task, ai_advice:
        lattice_rank(gateway_verdict(action, ai_advice)) >= lattice_rank(gateway_verdict(action, offline_baseline))

The gateway evaluates whole actions across AI modes against the offline rules baseline.
"""

import pytest
from src.types import ActionRequest, Verdict, ContextSource
from src.reference_gateway import ReferenceGateway

RANK = {Verdict.ALLOW: 1, Verdict.HOLD: 2, Verdict.BLOCK: 3}

# Representative suite of whole actions spanning all policy branches
ACTIONS_CORPUS = [
    # 1. Low-value payment (Baseline: ALLOW)
    (
        ActionRequest(
            agent_id="agent-001",
            action_type="process_payment",
            arguments={"amount": 4000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
            requested_by="riya",
        ),
        "TASK-DISP-101",
        "low_value_auto_allow",
    ),
    # 2. Mid-value payment (Baseline: HOLD)
    (
        ActionRequest(
            agent_id="agent-001",
            action_type="process_payment",
            arguments={"amount": 25000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
            requested_by="riya",
        ),
        "TASK-DISP-101",
        "mid_value_payment_hold",
    ),
    # 3. High-value payment exceeding limit (Baseline: BLOCK)
    (
        ActionRequest(
            agent_id="agent-001",
            action_type="process_payment",
            arguments={"amount": 150000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
            requested_by="riya",
        ),
        "TASK-DISP-101",
        "high_value_payment_block",
    ),
    # 4. Out-of-scope action for task (Baseline: BLOCK)
    (
        ActionRequest(
            agent_id="agent-001",
            action_type="export_records",
            arguments={"target_entity": "employees", "record_count": 10},
            requested_by="riya",
        ),
        "TASK-DISP-101",
        "task_scope_violation_block",
    ),
    # 5. Unknown rogue agent (Baseline: BLOCK)
    (
        ActionRequest(
            agent_id="rogue-agent-999",
            action_type="process_payment",
            arguments={"amount": 500.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
            requested_by="riya",
        ),
        "TASK-DISP-101",
        "unknown_agent_block",
    ),
    # 6. Supplier master update (Baseline: HOLD)
    (
        ActionRequest(
            agent_id="agent-001",
            action_type="update_supplier",
            arguments={"supplier_id": "SUP-001", "new_bank_account": "HDFC-00129834"},
            requested_by="riya",
        ),
        "TASK-ADMIN-404",
        "supplier_modification_hold",
    ),
    # 7. Untrusted argument origin (Baseline: HOLD)
    (
        ActionRequest(
            agent_id="agent-001",
            action_type="process_payment",
            arguments={"amount": 8000.0, "bank_account": "UNVERIFIED-ACCT-77", "supplier_id": "SUP-001"},
            requested_by="riya",
            context_sources=(ContextSource("invoice_pdf", "INV-1", "Pay UNVERIFIED-ACCT-77", trusted=False),),
        ),
        "TASK-DISP-101",
        "untrusted_origin_hold",
    ),
]


@pytest.mark.parametrize("action,task_id,scenario_label", ACTIONS_CORPUS)
@pytest.mark.parametrize("injected_ai_verdict", [Verdict.ALLOW, Verdict.HOLD, Verdict.BLOCK])
def test_p1_gateway_lattice_invariant(action, task_id, scenario_label, injected_ai_verdict):
    """
    Evaluates whole actions through the gateway wiring.
    Verifies that for every action and every injected AI verdict,
    the gateway's arbitrated verdict never relaxes the AI-offline baseline verdict.
    """
    # Baseline: Run through gateway with AI offline
    gateway_offline = ReferenceGateway(ai_mode="offline")
    dec_baseline = gateway_offline.evaluate(action, task_id)
    baseline_verdict = dec_baseline.verdict

    # Active Test: Run through gateway with injected AI advice
    gateway_active = ReferenceGateway()
    gateway_active._injectAIResponse(injected_ai_verdict)
    dec_active = gateway_active.evaluate(action, task_id)
    active_verdict = dec_active.verdict

    # Core Security Invariant: rank(active) >= rank(baseline)
    assert RANK[active_verdict] >= RANK[baseline_verdict], (
        f"LATTICE VIOLATION in scenario '{scenario_label}'! "
        f"Offline Baseline was {baseline_verdict}, but AI advice {injected_ai_verdict} "
        f"caused gateway to relax to {active_verdict}."
    )

    # Specific safety constraints:
    # If baseline is BLOCK, active verdict must be BLOCK
    if baseline_verdict == Verdict.BLOCK:
        assert active_verdict == Verdict.BLOCK

    # If baseline is HOLD, active verdict can NEVER be ALLOW
    if baseline_verdict == Verdict.HOLD:
        assert active_verdict in (Verdict.HOLD, Verdict.BLOCK)
