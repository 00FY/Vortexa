"""HTTP Adapter Smoke Tests: Verifying Gateway Contract & Attack Lifecycle over REST API."""

import pytest
from fastapi.testclient import TestClient
from src.http_adapter import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_gateway_state():
    client.post("/reset")


def test_http_health_and_tasks():
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_tasks = client.get("/tasks")
    assert res_tasks.status_code == 200
    tasks = res_tasks.json()
    assert any(t["task_id"] == "TASK-DISP-101" for t in tasks)


def test_http_attack_unknown_agent_blocked():
    payload = {
        "action": {
            "agent_id": "rogue-agent-999",
            "action_type": "process_payment",
            "arguments": {"amount": 5000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
            "requested_by": "riya",
            "context_sources": [],
            "metadata": {},
        },
        "task_id": "TASK-DISP-101",
    }
    res = client.post("/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["verdict"] == "BLOCK"
    assert data["error_code"] == "ERR_UNKNOWN_AGENT"


def test_http_t04_modified_payload_invalidates_approval():
    # Step 1: Evaluate ₹15,000 payment -> HELD
    action_data = {
        "agent_id": "agent-001",
        "action_type": "process_payment",
        "arguments": {"amount": 15000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        "requested_by": "riya",
        "context_sources": [],
        "metadata": {},
    }
    eval_res = client.post("/evaluate", json={"action": action_data, "task_id": "TASK-DISP-101"})
    assert eval_res.status_code == 200
    action_id = eval_res.json()["action_id"]
    action_hash = eval_res.json()["action_hash"]
    assert eval_res.json()["verdict"] == "HOLD"

    # Step 2: Approve with Karan's authenticated token
    appr_payload = {
        "approver_id": "karan",
        "token": "TOK-KARAN-SECRET",
        "role": "kyc_officer",
        "action_hash": action_hash,
    }
    appr_res = client.post(f"/approve/{action_id}", json=appr_payload)
    assert appr_res.status_code == 200
    assert appr_res.json()["verdict"] == "ALLOW"

    status_res = client.get(f"/status/{action_id}")
    assert status_res.json()["status"] == "APPROVED"

    # Step 3: Execute with tampered payload -> ERR_HASH_MISMATCH
    tampered_action = dict(action_data)
    tampered_action["arguments"] = {"amount": 95000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"}

    exec_res = client.post(f"/execute/{action_id}", json={"action": tampered_action})
    assert exec_res.status_code == 200
    assert exec_res.json()["success"] is False
    assert exec_res.json()["error_code"] == "ERR_HASH_MISMATCH"

    # Step 4: Status transitioned permanently to INVALIDATED
    status_invalidated = client.get(f"/status/{action_id}")
    assert status_invalidated.json()["status"] == "INVALIDATED"


def test_http_t05_wrong_hash_approval_refused_leaves_held():
    # Step 1: Evaluate ₹20,000 payment -> HELD
    action_data = {
        "agent_id": "agent-001",
        "action_type": "process_payment",
        "arguments": {"amount": 20000.0, "bank_account": "HDFC-00129834", "supplier_id": "SUP-001"},
        "requested_by": "riya",
        "context_sources": [],
        "metadata": {},
    }
    eval_res = client.post("/evaluate", json={"action": action_data, "task_id": "TASK-DISP-101"})
    action_id = eval_res.json()["action_id"]

    # Step 2: Adversary attempts approval with fabricated wrong hash
    bad_appr_payload = {
        "approver_id": "karan",
        "token": "TOK-KARAN-SECRET",
        "role": "kyc_officer",
        "action_hash": "0000000000000000000000000000000000000000000000000000000000000000",
    }
    bad_res = client.post(f"/approve/{action_id}", json=bad_appr_payload)
    assert bad_res.status_code == 200
    assert bad_res.json()["verdict"] == "HOLD"
    assert bad_res.json()["error_code"] == "ERR_HASH_MISMATCH"

    # Crucial DoS check: Action remains HELD (not killed/blocked)
    status_res = client.get(f"/status/{action_id}")
    assert status_res.json()["status"] == "HELD"
