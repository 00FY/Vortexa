"""
agents/llm/provider.py
----------------------
Configurable LLM provider for the ActionGate AI orchestration layer.

Modes
-----
LLM_PROVIDER=mock  (default)
    Deterministic regex / keyword logic. Zero API cost. 100% reproducible.
    Required for unit tests — all 22 existing tests run entirely offline.

LLM_PROVIDER=openai
    Uses ChatOpenAI (langchain_openai) for intent classification and
    structured field extraction (function calling / with_structured_output).
    Requires OPENAI_API_KEY. Model is configurable via OPENAI_MODEL.
    If the API is unavailable, raises LLMUnavailableError — never silently
    falls back to another provider or allows protected writes to proceed.

Security notes
--------------
- Model output is always validated through Pydantic schemas.
- Model output is treated as untrusted input even when schema-conformant.
- Input is truncated before being sent to the LLM (prompt-injection is
  defense-in-depth; deterministic server-side guards are the real boundary).
- Secrets (API key) are read from environment variables and never logged.
"""

import re
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class LLMUnavailableError(Exception):
    """
    Raised when the configured LLM provider is unavailable, returns an
    unusable response, or is configured but lacks credentials.

    Callers (graph nodes) must catch this and return a fail-closed error
    state — no protected write may proceed without a valid LLM response
    when LLM_PROVIDER != mock.
    """


# ---------------------------------------------------------------------------
# Structured output schemas  (used with OpenAI function calling)
# ---------------------------------------------------------------------------

class LeaveFields(BaseModel):
    """Structured leave request fields extracted from natural language."""
    start_date: Optional[str] = Field(
        None,
        description=(
            "Start date in YYYY-MM-DD format. "
            "Convert relative expressions (e.g. 'next Monday', 'tomorrow') "
            "to absolute dates, treating today as 2026-10-12."
        ),
    )
    end_date: Optional[str] = Field(
        None,
        description="End date in YYYY-MM-DD. Equal to start_date if not stated explicitly.",
    )
    leave_type: Optional[str] = Field(
        None,
        description="One of: ANNUAL, SICK, CASUAL, MATERNITY, PATERNITY, UNPAID. Null if not mentioned.",
    )
    reason: Optional[str] = Field(
        None,
        description="Brief business reason for the leave request. Null if not stated.",
    )


class ExpenseFields(BaseModel):
    """Structured expense claim fields extracted from natural language."""
    amount: Optional[float] = Field(
        None,
        description="Numeric expense amount (e.g. 4500.0 for ₹4,500). Null if not mentioned.",
    )
    currency: str = Field("INR", description="Currency code. Default INR.")
    category: Optional[str] = Field(
        None,
        description=(
            "Expense category — one of: TRAVEL, MEALS, EQUIPMENT, SOFTWARE, OFFICE, "
            "TRAINING, MISC. Infer from context (e.g. 'cab fare' → TRAVEL). Null if unclear."
        ),
    )
    description: Optional[str] = Field(
        None,
        description="Business purpose / description of the expense. Null if not stated.",
    )


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

_INTENT_SYSTEM_PROMPT = """You are an intent classifier for a Mini ERP assistant.

Classify the user's message into exactly one of these business domains:
- LEAVE     : leave requests, vacation, time off, sick days, leave history / balance
- FINANCE   : expense claims, reimbursements, expense submissions, expense approvals
- HR        : employee profiles, company directory, team lookups, manager info
- GENERAL_QUERY : anything else, unclear, or out of scope

Rules:
1. Respond with ONLY the intent label in UPPERCASE (e.g. LEAVE).
2. Never include explanations, punctuation, or extra words.
3. If unsure, return GENERAL_QUERY."""


# ---------------------------------------------------------------------------
# Main provider class
# ---------------------------------------------------------------------------

class LLMProvider:
    """
    Unified LLM interface used by graph nodes and specialist agents.

    Public API
    ----------
    classify_intent(message)           -> str
    extract_leave_fields(msg, ctx)     -> dict
    extract_expense_fields(msg, ctx)   -> dict
    is_available()                     -> bool
    """

    def __init__(self):
        # Lazy import avoids circular dependency at module load time
        from agents.config import settings
        self._settings = settings
        self.provider = settings.LLM_PROVIDER.lower()
        self.model_name = settings.LLM_MODEL
        self._client = None
        self._init_client()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_client(self):
        if self.provider != "openai":
            return  # Mock mode — no external client needed

        if not self._settings.OPENAI_API_KEY:
            logger.warning(
                "LLM_PROVIDER=openai but OPENAI_API_KEY is not configured. "
                "The LLM will be unavailable and all LLM-dependent requests "
                "will fail-closed (no protected write will proceed)."
            )
            return

        try:
            from langchain_openai import ChatOpenAI  # type: ignore
            self._client = ChatOpenAI(
                model=self.model_name,
                api_key=self._settings.OPENAI_API_KEY,
                temperature=0.0,
                timeout=30,
                # max_retries=1: only retry transient read errors.
                # Business mutations are never blindly retried when status is uncertain.
                max_retries=1,
            )
            logger.info("OpenAI client initialised: model=%s", self.model_name)
        except Exception as exc:
            logger.error("Failed to initialise OpenAI client: %s", exc)
            self._client = None

    def is_available(self) -> bool:
        """True when the provider is ready to serve requests."""
        if self.provider == "mock":
            return True
        return self._client is not None

    # ------------------------------------------------------------------
    # Intent classification
    # ------------------------------------------------------------------

    def classify_intent(self, message: str) -> str:
        """
        Classify user message into: LEAVE | FINANCE | HR | GENERAL_QUERY.

        Mock mode : deterministic regex (no network call).
        OpenAI mode: single ChatOpenAI call with validated enum output.

        Raises LLMUnavailableError if LLM_PROVIDER=openai and the API is
        unreachable or returns an unusable response.
        """
        if self.provider == "mock":
            return _regex_classify_intent(message)

        if not self.is_available():
            raise LLMUnavailableError(
                "OpenAI API is configured (LLM_PROVIDER=openai) but is currently "
                "unavailable (missing or invalid API key). Intent classification "
                "cannot proceed safely — protected operations are halted."
            )

        try:
            from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore

            # Truncate to limit prompt injection surface and token cost
            safe_message = message[:1500]

            response = self._client.invoke([
                SystemMessage(content=_INTENT_SYSTEM_PROMPT),
                HumanMessage(content=safe_message),
            ])

            # Validate against strict allowlist — treat model output as untrusted
            raw = response.content.strip().upper().split()[0] if response.content.strip() else ""
            allowed = {"LEAVE", "FINANCE", "HR", "GENERAL_QUERY"}
            if raw not in allowed:
                logger.warning(
                    "OpenAI returned unrecognised intent %r — defaulting to GENERAL_QUERY", raw
                )
                return "GENERAL_QUERY"
            return raw

        except LLMUnavailableError:
            raise
        except Exception as exc:
            raise LLMUnavailableError(
                f"OpenAI intent classification failed: {type(exc).__name__}: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Leave field extraction
    # ------------------------------------------------------------------

    def extract_leave_fields(
        self, message: str, conversation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract leave request fields from natural language.

        Mock mode : returns {} — specialist agent's regex handles extraction.
        OpenAI mode: structured output (function calling) → validated dict.

        Raises LLMUnavailableError if OpenAI is configured but unavailable.
        """
        if self.provider == "mock":
            return {}

        if not self.is_available():
            raise LLMUnavailableError("OpenAI unavailable for leave field extraction.")

        prev_slots = conversation_context.get("slots", {}) if conversation_context else {}
        context_note = f"\nPreviously collected fields: {prev_slots}" if prev_slots else ""

        try:
            from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore

            structured_llm = self._client.with_structured_output(LeaveFields)
            result: LeaveFields = structured_llm.invoke([
                SystemMessage(
                    content=(
                        "Extract structured leave request fields from the user's message. "
                        "Return null for any field not mentioned. "
                        "Never invent or assume values the user did not state."
                    )
                ),
                HumanMessage(
                    content=(
                        f"Extract leave request fields.{context_note}\n\n"
                        f"User message: {message[:1500]}"
                    )
                ),
            ])

            # Validate every field — model output is untrusted even when schema-conformant
            extracted: Dict[str, Any] = {}

            if result.start_date and isinstance(result.start_date, str):
                # Only accept YYYY-MM-DD format
                if re.match(r"^\d{4}-\d{2}-\d{2}$", result.start_date.strip()):
                    extracted["start_date"] = result.start_date.strip()

            if result.end_date and isinstance(result.end_date, str):
                if re.match(r"^\d{4}-\d{2}-\d{2}$", result.end_date.strip()):
                    extracted["end_date"] = result.end_date.strip()

            if result.leave_type and isinstance(result.leave_type, str):
                valid_types = {"ANNUAL", "SICK", "CASUAL", "MATERNITY", "PATERNITY", "UNPAID"}
                lt = result.leave_type.strip().upper()
                if lt in valid_types:
                    extracted["leave_type"] = lt

            if result.reason and isinstance(result.reason, str):
                reason = result.reason.strip()
                if len(reason) >= 3:
                    extracted["reason"] = reason[:200]  # Bound length

            return extracted

        except LLMUnavailableError:
            raise
        except Exception as exc:
            raise LLMUnavailableError(
                f"OpenAI leave field extraction failed: {type(exc).__name__}: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Expense field extraction
    # ------------------------------------------------------------------

    def extract_expense_fields(
        self, message: str, conversation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract expense claim fields from natural language.

        Mock mode : returns {} — specialist agent's regex handles extraction.
        OpenAI mode: structured output (function calling) → validated dict.

        Raises LLMUnavailableError if OpenAI is configured but unavailable.
        """
        if self.provider == "mock":
            return {}

        if not self.is_available():
            raise LLMUnavailableError("OpenAI unavailable for expense field extraction.")

        prev_slots = conversation_context.get("slots", {}) if conversation_context else {}
        context_note = f"\nPreviously collected fields: {prev_slots}" if prev_slots else ""

        try:
            from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore

            structured_llm = self._client.with_structured_output(ExpenseFields)
            result: ExpenseFields = structured_llm.invoke([
                SystemMessage(
                    content=(
                        "Extract structured expense claim fields from the user's message. "
                        "Return null for any field not mentioned. "
                        "Never invent or assume values the user did not state. "
                        "Always use INR as currency regardless of what the user says."
                    )
                ),
                HumanMessage(
                    content=(
                        f"Extract expense claim fields.{context_note}\n\n"
                        f"User message: {message[:1500]}"
                    )
                ),
            ])

            # Validate every field — model output is untrusted
            extracted: Dict[str, Any] = {}

            if result.amount is not None:
                try:
                    amt = float(result.amount)
                    # Sanity-range check: reject zero / negative / absurdly large amounts
                    if 0 < amt < 10_000_000:
                        extracted["amount"] = amt
                    else:
                        logger.warning("OpenAI returned out-of-range amount %r — discarded", amt)
                except (ValueError, TypeError):
                    pass

            if result.category and isinstance(result.category, str):
                valid_cats = {"TRAVEL", "MEALS", "EQUIPMENT", "SOFTWARE", "OFFICE", "TRAINING", "MISC"}
                cat = result.category.strip().upper()
                if cat in valid_cats:
                    extracted["category"] = cat
                else:
                    logger.warning("OpenAI returned unknown category %r — discarded", cat)

            if result.description and isinstance(result.description, str):
                desc = result.description.strip()
                if len(desc) >= 3:
                    extracted["description"] = desc[:300]  # Bound length

            # Currency is always INR — never derived from model output
            extracted["currency"] = "INR"

            return extracted

        except LLMUnavailableError:
            raise
        except Exception as exc:
            raise LLMUnavailableError(
                f"OpenAI expense field extraction failed: {type(exc).__name__}: {exc}"
            ) from exc


# ---------------------------------------------------------------------------
# Deterministic regex fallback  (mock mode)
# ---------------------------------------------------------------------------

def _regex_classify_intent(message: str) -> str:
    """
    Keyword-based intent classification — used when LLM_PROVIDER=mock.
    Deterministic, zero-cost, no network required.
    """
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ["leave", "vacation", "time off", "sick day", "annual leave"]):
        return "LEAVE"
    if any(kw in msg_lower for kw in ["expense", "claim", "reimbursement", "approve"]):
        return "FINANCE"
    if any(kw in msg_lower for kw in ["profile", "directory", "colleague", "department", "manager"]):
        return "HR"
    return "GENERAL_QUERY"


def parse_relative_date(text: str) -> Optional[str]:
    """
    Convert relative date expressions to YYYY-MM-DD.
    Reference date: 2026-10-12 (demo baseline).
    Used by LeaveAgent regex path.
    """
    text_lower = text.lower()
    ref_date = datetime(2026, 10, 12)

    if "next monday" in text_lower:
        return (ref_date + timedelta(days=7)).strftime("%Y-%m-%d")
    if "tomorrow" in text_lower:
        return (ref_date + timedelta(days=1)).strftime("%Y-%m-%d")
    if "today" in text_lower:
        return ref_date.strftime("%Y-%m-%d")

    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if match:
        return match.group(1)

    return None
