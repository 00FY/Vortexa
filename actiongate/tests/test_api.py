from starlette.testclient import TestClient
from actiongate.api.app import app
from actiongate.types import calculate_action_fingerprint


def test_health_check_endpoint():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"


def test_evaluate_endpoint_allow():
    client = TestClient(app)
    req = {
        "request_id": "REQ-API-001",
        "action_type": "leave.get_history",
        "target_resource": "leaves:EMP-001",
        "parameters": {"employee_id": "EMP-001"},
        "requester_id": "EMP-001",
        "requester_role": "EMPLOYEE",
        "action_fingerprint": "fp-123",
    }
    resp = client.post("/api/v1/evaluate", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "ALLOW"
    assert data["risk_score"] == 0.0


def test_evaluate_and_approval_workflow():
    client = TestClient(app)
    fp = calculate_action_fingerprint("expense.approve", "expense:EXP-999", {"amount": 25000.0}, "MGR-002")

    req = {
        "request_id": "REQ-API-002",
        "action_type": "expense.approve",
        "target_resource": "expense:EXP-999",
        "parameters": {"amount": 25000.0, "claimant_id": "EMP-001"},
        "requester_id": "MGR-002",
        "requester_role": "MANAGER",
        "action_fingerprint": fp,
    }

    # Step 1: Pre-approval -> HOLD
    resp1 = client.post("/api/v1/evaluate", json=req)
    assert resp1.status_code == 200
    assert resp1.json()["decision"] == "HOLD"
    dec_id = resp1.json()["decision_id"]

    # Step 2: Out-of-band Manager Approval registered
    approval_payload = {
        "decision_id": dec_id,
        "approver_id": "MGR-002",
        "approver_role": "MANAGER",
        "action_fingerprint": fp,
        "status": "APPROVED",
        "notes": "Verified client travel invoice",
    }
    app_resp = client.post("/api/v1/approvals", json=approval_payload)
    assert app_resp.status_code == 200

    # Step 3: Re-evaluation with exact fingerprint -> ALLOW
    resp2 = client.post("/api/v1/evaluate", json=req)
    assert resp2.status_code == 200
    assert resp2.json()["decision"] == "ALLOW"

    # Step 4: Verify audit trail
    audit_resp = client.get("/api/v1/audit")
    assert audit_resp.status_code == 200
    audit_data = audit_resp.json()
    assert audit_data["chain_valid"] is True
    assert audit_data["total_entries"] >= 3
