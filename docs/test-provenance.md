# Test Provenance: Verification Matrix

This document maps all automated tests and demo cases to their corresponding security controls and implementation files.

## 1. Test Matrix

| Case / Scenario | Test Method | Test Location | Status |
| :--- | :--- | :--- | :--- |
| **Case A: Leave Missing Slots & ALLOW** | `test_case_a_leave_application_flow` | `agents/tests/test_e2e_cases.py` | ✅ PASSED |
| **Case B: Self-Approval Blocked** | `test_case_b_self_approval_blocked` | `agents/tests/test_e2e_cases.py` | ✅ PASSED |
| **Case C: HOLD & Exact-Action Sign-off** | `test_case_c_hold_and_exact_approval_flow` | `agents/tests/test_e2e_cases.py` | ✅ PASSED |
| **Case D: Parameter Tampering Rejected** | `test_case_d_parameter_tampering_rejected` | `agents/tests/test_e2e_cases.py` | ✅ PASSED |
| **Case E: Prompt Injection Filtered** | `test_case_e_prompt_injection_rejected` | `agents/tests/test_e2e_cases.py` | ✅ PASSED |
| **Case F: ActionGate Outage Fail-Closed** | `test_case_f_actiongate_outage_fails_closed` | `agents/tests/test_e2e_cases.py` | ✅ PASSED |
| **Security: Identity Spoofing Rejection** | `test_security_requester_identity_spoofing_prevented` | `agents/tests/test_e2e_cases.py` | ✅ PASSED |
| **Schema: Action Catalog Allowlist** | `test_action_allowlist_valid`, `test_action_allowlist_unsupported` | `agents/tests/test_schemas.py` | ✅ PASSED |
| **Schema: Deterministic Fingerprint** | `test_deterministic_action_fingerprint` | `agents/tests/test_schemas.py` | ✅ PASSED |
| **API: Health & Chat Flow** | `test_api_health_endpoint`, `test_api_chat_leave_flow` | `agents/tests/test_api_endpoints.py` | ✅ PASSED |
| **API: Idempotency Caching** | `test_api_chat_idempotency` | `agents/tests/test_api_endpoints.py` | ✅ PASSED |
| **Agents: HR Profile & Directory** | `test_hr_profile_retrieval`, `test_hr_directory_lookup` | `agents/tests/test_agents_and_queries.py` | ✅ PASSED |
| **Agents: Leave & Expense Queries** | `test_leave_history_retrieval`, `test_expense_list_retrieval` | `agents/tests/test_agents_and_queries.py` | ✅ PASSED |
| **Agents: Expense Missing Slots & Create** | `test_expense_submit_missing_fields`, `test_expense_submit_successful` | `agents/tests/test_agents_and_queries.py` | ✅ PASSED |
| **Outage: ERP Backend Down** | `test_erp_backend_outage_fails_closed` | `agents/tests/test_agents_and_queries.py` | ✅ PASSED |

Total: **22/22 Automated Tests Passing**
