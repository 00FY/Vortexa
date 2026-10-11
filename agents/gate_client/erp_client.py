import httpx
import logging
from typing import Optional, List, Dict, Any
from agents.config import settings
from agents.schemas.erp import ERPExecutionResponse
from agents.gate_client.mocks import MockERP

logger = logging.getLogger(__name__)

class ERPClient:
    """
    Client for interacting with the Mini ERP business backend.
    Enforces authenticated session context and only calls approved business APIs.
    """
    def __init__(self, mock_instance: Optional[MockERP] = None):
        self.base_url = settings.ERP_BASE_URL
        self.timeout = settings.ERP_TIMEOUT_SECONDS
        self.use_mock = settings.USE_MOCKS
        self._mock = mock_instance or MockERP()

    def get_profile(self, employee_id: str, auth_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if self.use_mock:
            return self._mock.get_employee(employee_id)

        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/api/employees/{employee_id}", headers=headers)
            resp.raise_for_status()
            return resp.json()

    def search_directory(self, query: Optional[str] = None, department: Optional[str] = None, auth_token: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.use_mock:
            return self._mock.search_directory(query=query, department=department)

        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        params = {}
        if query:
            params["query"] = query
        if department:
            params["department"] = department
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/api/directory", params=params, headers=headers)
            resp.raise_for_status()
            return resp.json()

    def get_leave_history(self, employee_id: str, auth_token: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.use_mock:
            return self._mock.get_leave_history(employee_id)

        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/api/leaves/employee/{employee_id}", headers=headers)
            resp.raise_for_status()
            return resp.json()

    def create_leave_request(
        self,
        employee_id: str,
        leave_type: str,
        start_date: str,
        end_date: str,
        reason: str,
        auth_token: Optional[str] = None
    ) -> ERPExecutionResponse:
        if self.use_mock:
            return self._mock.create_leave(
                employee_id=employee_id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason
            )

        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        payload = {
            "employee_id": employee_id,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "reason": reason,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base_url}/api/leaves", json=payload, headers=headers)
            resp.raise_for_status()
            return ERPExecutionResponse.model_validate(resp.json())

    def get_expense_list(self, employee_id: str, auth_token: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.use_mock:
            return self._mock.get_expenses(employee_id)

        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/api/expenses/employee/{employee_id}", headers=headers)
            resp.raise_for_status()
            return resp.json()

    def submit_expense_claim(
        self,
        employee_id: str,
        amount: float,
        currency: str,
        category: str,
        description: str,
        auth_token: Optional[str] = None
    ) -> ERPExecutionResponse:
        if self.use_mock:
            return self._mock.submit_expense(
                employee_id=employee_id,
                amount=amount,
                currency=currency,
                category=category,
                description=description
            )

        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        payload = {
            "employee_id": employee_id,
            "amount": amount,
            "currency": currency,
            "category": category,
            "description": description,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base_url}/api/expenses", json=payload, headers=headers)
            resp.raise_for_status()
            return ERPExecutionResponse.model_validate(resp.json())

    def approve_expense_claim(
        self,
        expense_id: str,
        approver_id: str,
        decision: str,
        notes: Optional[str] = None,
        auth_token: Optional[str] = None
    ) -> ERPExecutionResponse:
        if self.use_mock:
            return self._mock.approve_expense(
                expense_id=expense_id,
                approver_id=approver_id,
                decision=decision,
                notes=notes
            )

        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        payload = {
            "expense_id": expense_id,
            "approver_id": approver_id,
            "decision": decision,
            "notes": notes,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base_url}/api/expenses/{expense_id}/approve", json=payload, headers=headers)
            resp.raise_for_status()
            return ERPExecutionResponse.model_validate(resp.json())

    def get_mock(self) -> MockERP:
        return self._mock
