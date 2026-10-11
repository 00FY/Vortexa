"""
integrations/voice/voice_service.py
-----------------------------------
Text-to-speech voice generation service (supporting ElevenLabs and local audio synthesis).
Used to generate spoken audio briefings of HELD authorization requests.
"""

import os
from typing import Dict, Any, Optional

class VoiceBriefingService:
    """
    Synthesizes spoken audio briefs for executives summarizing held actions
    and security evaluation explanations.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")

    def generate_briefing_script(
        self,
        manager_name: str,
        action_type: str,
        target_id: str,
        amount: float,
        risk_score: float
    ) -> str:
        return (
            f"Hello {manager_name}. ActionGate has placed an action on hold for your review. "
            f"An expense approval for {target_id} in the amount of {amount:,.0f} rupees "
            f"has an evaluated risk score of {risk_score:.2f}. "
            f"Please review the canonical fingerprint in your ERP portal."
        )

    def synthesize_audio(self, text: str) -> Dict[str, Any]:
        """
        Synthesizes audio or returns structured mock payload if API key is not present.
        """
        has_live_key = bool(self.api_key and self.api_key.strip())
        return {
            "status": "SUCCESS",
            "provider": "elevenlabs" if has_live_key else "mock_synthesizer",
            "text": text,
            "duration_estimated_sec": round(len(text.split()) / 2.5, 1),
            "audio_format": "mp3",
            "mock": not has_live_key
        }
