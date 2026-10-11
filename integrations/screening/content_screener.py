"""
integrations/screening/content_screener.py
-----------------------------------------
Ingestion content screening adapter for inspecting external documents,
emails, and user prompts before passing to conversational agents.
"""

import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ScreeningResult(BaseModel):
    is_safe: bool
    risk_flags: List[str]
    sanitized_content: str
    confidence: float

_ADVERSARIAL_PATTERNS = [
    (r"\[INST:.*?\]", "Synthetic instruction injection tokens"),
    (r"ignore\s+(all\s+)?(previous\s+)?instructions", "Instruction override attempt"),
    (r"grant\s+(admin|root|superuser)", "Privilege escalation syntax"),
    (r"drop\s+table", "SQL injection pattern"),
    (r"bypass\s+actiongate", "Security boundary bypass attempt"),
]

class ContentScreener:
    """
    Ingestion scanner evaluating untrusted content for embedded attacks,
    prompt injections, and toxic commands.
    """
    def screen_text(self, text: str) -> ScreeningResult:
        flags = []
        for pattern, desc in _ADVERSARIAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                flags.append(desc)

        is_safe = len(flags) == 0
        return ScreeningResult(
            is_safe=is_safe,
            risk_flags=flags,
            sanitized_content=text if is_safe else "[FILTERED_ADVERSARIAL_CONTENT]",
            confidence=1.0 if not is_safe else 0.95
        )
