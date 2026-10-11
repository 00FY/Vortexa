# Enterprise AI Orchestration Security Invariants

1. **Zero-Trust Caller Identity**:
   - Never accept user IDs, roles, or permissions from natural-language prompts, LLM parameters, or client-side form fields.
   - Always bind identities server-side from verified session contexts (e.g., validated JWTs or authenticated ERP context).

2. **Canonical Action Fingerprinting**:
   - Sign all sensitive action proposals using a deterministic hash (SHA-256 over canonical JSON with sorted keys).
   - Any modification to parameters, target, or requester invalidates existing authorization decisions.

3. **Separation of Conversational Intent vs. Formal Approval**:
   - Do not treat conversational responses ("yes", "approved") as formal corporate authorization for sensitive operations.
   - Sensitive operations must transition to `HOLD` and direct users to authorized ERP/business workflows.

4. **Fail-Closed Execution**:
   - If authorization services (e.g. ActionGate), LLMs, or downstream business APIs become unavailable, immediately halt protected mutations and report safe unavailability. Never fail open.

5. **Allowlist-Only Execution**:
   - Agents must never have direct database access (PostgreSQL), raw SQL execution, or arbitrary tool dispatch.
