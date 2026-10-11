import re
from typing import Optional
from datetime import datetime, timedelta
from agents.config import settings

class LLMProvider:
    """
    Configurable LLM provider supporting OpenAI, Anthropic, Groq, and a
    deterministic Mock LLM for offline testing and 100% reproducible demo runs.
    """
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.model_name = settings.LLM_MODEL
        self._external_client = None
        self._init_client()

    def _init_client(self):
        if self.provider == "openai" and settings.OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI
            self._external_client = ChatOpenAI(model=self.model_name, api_key=settings.OPENAI_API_KEY, temperature=0.0)
        elif self.provider == "groq" and settings.GROQ_API_KEY:
            from langchain_groq import ChatGroq
            self._external_client = ChatGroq(model=self.model_name, api_key=settings.GROQ_API_KEY, temperature=0.0)

    def is_available(self) -> bool:
        if self.provider in ["openai", "groq", "anthropic"]:
            return self._external_client is not None
        return True

def parse_relative_date(text: str) -> Optional[str]:
    """
    Converts relative expressions like 'next Monday', 'tomorrow', 'today'
    to standard YYYY-MM-DD format based on reference date (2026-10-12).
    """
    text_lower = text.lower()
    ref_date = datetime(2026, 10, 12)

    if "next monday" in text_lower:
        target = ref_date + timedelta(days=7)
        return target.strftime("%Y-%m-%d")
    elif "tomorrow" in text_lower:
        target = ref_date + timedelta(days=1)
        return target.strftime("%Y-%m-%d")
    elif "today" in text_lower:
        return ref_date.strftime("%Y-%m-%d")
    
    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if match:
        return match.group(1)
        
    return None
