import httpx
import logging
from typing import Optional
from agents.config import settings
from agents.schemas.actiongate import ActionGateRequest, ActionGateDecision
from agents.gate_client.mocks import MockActionGate

logger = logging.getLogger(__name__)

class ActionGateClient:
    """
    Client for communicating with the ActionGate deterministic authorization engine.
    Ensures fail-closed behavior: an unavailable ActionGate never results in unauthorized execution.
    """
    def __init__(self, mock_instance: Optional[MockActionGate] = None):
        self.base_url = settings.ACTIONGATE_BASE_URL
        self.api_key = settings.ACTIONGATE_API_KEY
        self.timeout = settings.ACTIONGATE_TIMEOUT_SECONDS
        self.use_mock = settings.USE_MOCKS
        self._mock = mock_instance or MockActionGate()

    def evaluate_proposal(self, request: ActionGateRequest) -> ActionGateDecision:
        if self.use_mock:
            return self._mock.evaluate(request)

        try:
            with httpx.Client(timeout=self.timeout) as client:
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                response = client.post(
                    f"{self.base_url}/api/v1/evaluate",
                    json=request.model_dump(),
                    headers=headers
                )
                response.raise_for_status()
                return ActionGateDecision.model_validate(response.json())
        except Exception as e:
            logger.error(f"ActionGate communication failure: {e}")
            raise ConnectionError(f"ActionGate unavailable: {str(e)}")

    def get_mock(self) -> MockActionGate:
        return self._mock
