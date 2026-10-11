import pytest
from agents.schemas.erp import ERPUserContext, ERPUserRole
from agents.gate_client.mocks import MockERP, MockActionGate
from agents.gate_client.erp_client import ERPClient
from agents.gate_client.actiongate_client import ActionGateClient
from agents.graph.workflow import create_orchestrator_graph

@pytest.fixture
def mock_erp():
    erp = MockERP()
    erp.reset()
    return erp

@pytest.fixture
def mock_actiongate(mock_erp):
    ag = MockActionGate(erp_backend=mock_erp)
    ag.reset()
    return ag

@pytest.fixture
def erp_client(mock_erp):
    return ERPClient(mock_instance=mock_erp)

@pytest.fixture
def actiongate_client(mock_actiongate):
    return ActionGateClient(mock_instance=mock_actiongate)

@pytest.fixture
def orchestrator(actiongate_client, erp_client):
    return create_orchestrator_graph(
        actiongate_client=actiongate_client,
        erp_client=erp_client
    )

@pytest.fixture
def employee_user():
    return ERPUserContext(
        employee_id="EMP-001",
        name="Rahul Sharma",
        email="rahul.sharma@corp.mini-erp.com",
        role=ERPUserRole.EMPLOYEE,
        department="Engineering",
        manager_id="MGR-002",
        token="jwt-token-emp-001"
    )

@pytest.fixture
def manager_user():
    return ERPUserContext(
        employee_id="MGR-002",
        name="Vikram Malhotra",
        email="vikram.malhotra@corp.mini-erp.com",
        role=ERPUserRole.MANAGER,
        department="Engineering",
        manager_id="DIR-001",
        token="jwt-token-mgr-002"
    )
