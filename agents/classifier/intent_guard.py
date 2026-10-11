import re
from typing import Tuple, Optional

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous\s+)?instructions",
    r"system\s*prompt",
    r"grant\s+(admin|root|superuser)",
    r"drop\s+table",
    r"select\s+\*\s+from",
    r"bypass\s+actiongate",
    r"skip\s+authorization",
    r"execute\s+raw\s+sql",
]

def scan_prompt_injection(message: str) -> Optional[str]:
    """
    Scans user input against known adversarial prompts and authorization bypass attempts.
    Returns error description if malicious pattern is detected, None otherwise.
    """
    msg_lower = message.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, msg_lower):
            return "Prohibited command or authorization override attempt detected."
    return None

def classify_user_intent(message: str) -> str:
    """
    Determines business domain intent from user message.
    """
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ["leave", "vacation", "time off", "sick day", "annual leave"]):
        return "LEAVE"
    elif any(kw in msg_lower for kw in ["expense", "claim", "reimbursement", "approve"]):
        return "FINANCE"
    elif any(kw in msg_lower for kw in ["profile", "directory", "colleague", "department", "manager"]):
        return "HR"
    return "GENERAL_QUERY"
