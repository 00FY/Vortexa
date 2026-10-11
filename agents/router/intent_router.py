from typing import Dict, Any
from agents.classifier.intent_guard import scan_prompt_injection, classify_user_intent

def route_request(user_message: str) -> Dict[str, Any]:
    """
    Evaluates safety of input and returns target route metadata.
    """
    injection_err = scan_prompt_injection(user_message)
    if injection_err:
        return {
            "intent": "MALICIOUS_INPUT",
            "is_blocked": True,
            "error": injection_err,
            "refusal_message": (
                "Security Notice: Instructions attempting to override system authorization "
                "policies or execute arbitrary commands are strictly blocked."
            )
        }

    intent = classify_user_intent(user_message)
    return {
        "intent": intent,
        "is_blocked": False,
        "error": None,
        "refusal_message": None
    }
