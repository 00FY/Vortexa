"""
agents/tests/test_live_openai_smoke.py
----------------------------------------
Optional live-API smoke tests — only run when explicitly configured.

These tests make REAL OpenAI API calls and require:
  - LLM_PROVIDER=openai
  - OPENAI_API_KEY set to a valid key

They are automatically SKIPPED in all other environments, ensuring the
default test suite never depends on network access or API credits.

Run them explicitly:
  LLM_PROVIDER=openai OPENAI_API_KEY=sk-... pytest agents/tests/test_live_openai_smoke.py -v

Each test makes exactly one or two API calls to verify:
  1. Intent classification returns a recognised label
  2. Leave field extraction returns a structured result
  3. Expense field extraction returns a structured result
  4. LLM unavailability (bad key) raises LLMUnavailableError and the
     orchestrator fails closed with no protected write
"""

import os
import pytest
from agents.config import settings

# Skip the entire module unless we are intentionally running live tests
pytestmark = pytest.mark.skipif(
    settings.LLM_PROVIDER.lower() != "openai" or not settings.OPENAI_API_KEY,
    reason=(
        "Live OpenAI smoke tests skipped — "
        "set LLM_PROVIDER=openai and OPENAI_API_KEY to run"
    ),
)


@pytest.fixture(scope="module")
def live_llm():
    """LLMProvider initialised in openai mode with a real key."""
    from agents.llm.provider import LLMProvider
    return LLMProvider()


# ── 1. Intent classification ──────────────────────────────────────────────────

def test_live_classify_leave_intent(live_llm):
    intent = live_llm.classify_intent("I need to take a day off next Friday")
    assert intent == "LEAVE", f"Expected LEAVE, got {intent!r}"


def test_live_classify_finance_intent(live_llm):
    intent = live_llm.classify_intent("Submit ₹3,500 meal expense for client dinner")
    assert intent == "FINANCE", f"Expected FINANCE, got {intent!r}"


def test_live_classify_hr_intent(live_llm):
    intent = live_llm.classify_intent("Who is in the engineering team?")
    assert intent == "HR", f"Expected HR, got {intent!r}"


# ── 2. Leave field extraction ─────────────────────────────────────────────────

def test_live_extract_leave_fields(live_llm):
    fields = live_llm.extract_leave_fields(
        "I want annual leave from 2026-10-20 to 2026-10-22 for a family trip",
        {},
    )
    assert "start_date" in fields, f"Missing start_date in {fields}"
    assert fields["start_date"] == "2026-10-20"
    assert "leave_type" in fields
    assert fields["leave_type"] == "ANNUAL"


# ── 3. Expense field extraction ───────────────────────────────────────────────

def test_live_extract_expense_fields(live_llm):
    fields = live_llm.extract_expense_fields(
        "Submit ₹4,500 travel expense for cab to client site",
        {},
    )
    assert "amount" in fields, f"Missing amount in {fields}"
    assert abs(fields["amount"] - 4500.0) < 1.0
    assert fields.get("category") == "TRAVEL"
    assert fields.get("currency") == "INR"


# ── 4. Bad key → fail-closed in orchestrator ─────────────────────────────────

def test_live_bad_key_fails_closed(employee_user, mock_erp):
    """
    With an invalid API key, the orchestrator must return ERROR and
    perform no protected ERP mutations.
    """
    import os
    from agents.llm.provider import LLMProvider, LLMUnavailableError
    from agents.graph import nodes as _nodes
    from agents.gate_client.mocks import MockERP, MockActionGate
    from agents.gate_client.erp_client import ERPClient
    from agents.gate_client.actiongate_client import ActionGateClient
    from agents.graph.workflow import create_orchestrator_graph
    from agents.graph.state import ChatState

    # Temporarily override settings to use an invalid key
    original_key = _nodes.llm_provider._settings.OPENAI_API_KEY
    _nodes.llm_provider._settings.__dict__["OPENAI_API_KEY"] = "sk-invalid-key-for-test"

    # Re-initialise client with bad key
    _nodes.llm_provider._init_client()
    initial_leave_count = len(mock_erp.leaves)

    erp_client = ERPClient(mock_instance=mock_erp)
    ag_client = ActionGateClient(mock_instance=MockActionGate(erp_backend=mock_erp))
    orchestrator = create_orchestrator_graph(actiongate_client=ag_client, erp_client=erp_client)

    try:
        state: ChatState = {
            "user_message": "Apply for annual leave next Monday for doctor visit",
            "user_context": employee_user,
        }
        result = orchestrator.invoke(state)

        # System must fail-closed
        assert result["status"] == "ERROR"
        assert result.get("execution_result") is None
        assert len(mock_erp.leaves) == initial_leave_count
    finally:
        # Restore
        _nodes.llm_provider._settings.__dict__["OPENAI_API_KEY"] = original_key
        _nodes.llm_provider._init_client()
