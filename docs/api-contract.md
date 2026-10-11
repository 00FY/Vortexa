# API Contract: ActionGate Orchestrator & Integrations

## 1. Orchestrator Endpoint Contract

### `POST /api/chat`
Invoked by the Mini ERP Chatbot component when an authenticated user sends a natural-language message.

#### Request Schema
```json
{
  "message": "Apply for annual leave next Monday for doctor visit",
  "session_id": "sess-uuid-optional",
  "request_id": "req-uuid-optional",
  "user_context": {
    "employee_id": "EMP-001",
    "name": "Rahul Sharma",
    "email": "rahul.sharma@corp.mini-erp.com",
    "role": "EMPLOYEE",
    "department": "Engineering",
    "manager_id": "MGR-002",
    "token": "jwt-bearer-token"
  },
  "conversation_context": {
    "slots": {
      "start_date": "2026-10-19"
    }
  }
}
```

#### Response Schema
```json
{
  "request_id": "REQ-7D1B9A2F",
  "session_id": "SESS-3E8C4A10",
  "status": "SUCCESS",
  "response": "✅ **Leave Request Created Successfully**\n- **Leave ID**: `LV-1002`\n...",
  "decision": "ALLOW",
  "decision_id": "DEC-9A4B8C1D",
  "risk_score": 0.1,
  "action_type": "leave.create",
  "action_fingerprint": "7e3b1c55d045a1f...",
  "missing_fields": null
}
```

---

## 2. ActionGate Integration Contract

### `POST /api/v1/evaluate`
Submitted by the orchestrator to evaluate an exact proposed action before execution.

#### Request Schema
```json
{
  "request_id": "REQ-7D1B9A2F",
  "action_type": "expense.approve",
  "target_resource": "EXP-101",
  "parameters": {
    "expense_id": "EXP-101",
    "approver_id": "MGR-002",
    "decision": "APPROVE"
  },
  "requester_id": "MGR-002",
  "requester_role": "MANAGER",
  "requester_department": "Engineering",
  "action_fingerprint": "b5c3ddda1bcdcf3b412f0415d33604fca420126aabb8881e161878ef906926cf",
  "timestamp": "2026-10-11T10:00:00Z"
}
```

#### Response Schema
```json
{
  "decision_id": "DEC-07A903FA",
  "request_id": "REQ-7D1B9A2F",
  "decision": "HOLD",
  "risk_score": 0.6,
  "risk_level": "HIGH",
  "reasons": [
    "High-value expense approval requires out-of-band manager sign-off via ERP approval workflow."
  ],
  "action_fingerprint": "b5c3ddda1bcdcf3b412f0415d33604fca420126aabb8881e161878ef906926cf",
  "approval_required_role": "MANAGER",
  "hold_details": {
    "approval_workflow": "ERP_MANAGER_APPROVAL",
    "required_role": "MANAGER",
    "workflow_url": "/erp/approvals/expenses/EXP-101",
    "instructions": "Direct user to the ERP Approval Portal."
  }
}
```

---

## 3. Mini ERP Business Backend Contract

### Supported Business Operations
- `GET /api/employees/{employee_id}`
- `GET /api/directory?query={q}&department={dept}`
- `GET /api/leaves/employee/{employee_id}`
- `POST /api/leaves`
- `GET /api/expenses/employee/{employee_id}`
- `POST /api/expenses`
- `POST /api/expenses/{expense_id}/approve`
