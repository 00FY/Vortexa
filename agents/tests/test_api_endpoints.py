import pytest
from fastapi.testclient import TestClient
from agents.main import app

client = TestClient(app)

def test_api_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "actiongate-ai-agents"

def test_api_chat_leave_flow():
    resp1 = client.post(
        "/api/chat",
        json={"message": "Apply for leave next Monday"}
    )
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] == "NEEDS_CLARIFICATION"
    assert "leave_type" in data1["missing_fields"]

    resp2 = client.post(
        "/api/chat",
        json={
            "message": "Apply for annual leave next Monday for personal matters",
            "session_id": data1["session_id"]
        }
    )
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "SUCCESS"
    assert data2["decision"] == "ALLOW"
    assert "Leave Request Created Successfully" in data2["response"]

def test_api_chat_idempotency():
    req_id = "IDEMP-TEST-999"
    payload = {
        "request_id": req_id,
        "message": "View my profile",
    }
    
    resp1 = client.post("/api/chat", json=payload)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] == "SUCCESS"

    resp2 = client.post("/api/chat", json=payload)
    assert resp2.status_code == 200
    data2 = resp2.json()
    
    assert data1["request_id"] == data2["request_id"]
    assert data1["response"] == data2["response"]
