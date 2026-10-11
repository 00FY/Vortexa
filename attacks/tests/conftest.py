"""Shared pytest fixtures for the ActionGate Attacker Side test suite."""

import os
import sys
from pathlib import Path
import importlib
import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root / "attacks" / "reference"))
sys.path.insert(0, str(_repo_root / "actiongate-attacks"))
sys.path.insert(0, str(_repo_root))

from src.erp_state import ERPState
from src.types import Principal, PrincipalType


# Authenticated Principals
KARAN_PRINCIPAL = Principal("karan", PrincipalType.HUMAN_USER, "kyc_officer", "TOK-KARAN-SECRET")
RIYA_PRINCIPAL = Principal("riya", PrincipalType.HUMAN_USER, "dispute_operator", "TOK-RIYA-SECRET")
MEERA_PRINCIPAL = Principal("meera", PrincipalType.HUMAN_USER, "collections_officer", "TOK-MEERA-SECRET")
ADMIN_PRINCIPAL = Principal("admin", PrincipalType.HUMAN_USER, "admin_officer", "TOK-ADMIN-SECRET")
AGENT_PRINCIPAL = Principal("agent-001", PrincipalType.AGENT, "dispute_agent", "TOK-AGENT-001")


@pytest.fixture
def erp():
    return ERPState()


@pytest.fixture
def gateway(erp):
    # Dynamically select gateway implementation via GATEWAY_IMPL env var for mutation testing
    spec = os.environ.get("GATEWAY_IMPL", "src.reference_gateway:ReferenceGateway")
    module_name, class_name = spec.split(":")
    mod = importlib.import_module(module_name)
    cls = getattr(mod, class_name)
    return cls(erp_state=erp)


@pytest.fixture
def karan():
    return KARAN_PRINCIPAL


@pytest.fixture
def riya():
    return RIYA_PRINCIPAL


@pytest.fixture
def meera():
    return MEERA_PRINCIPAL


@pytest.fixture
def admin_user():
    return ADMIN_PRINCIPAL


@pytest.fixture
def rogue_agent_principal():
    return AGENT_PRINCIPAL


@pytest.fixture
def dispute_task_id():
    return "TASK-DISP-101"


@pytest.fixture
def kyc_task_id():
    return "TASK-KYC-202"


@pytest.fixture
def collections_task_id():
    return "TASK-COLL-303"


@pytest.fixture
def admin_task_id():
    return "TASK-ADMIN-404"
