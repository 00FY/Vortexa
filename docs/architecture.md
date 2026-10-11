# ActionGate: Architectural Specification

## 1. System Overview

ActionGate establishes a zero-trust authorization boundary between enterprise conversational AI agents and protected ERP business execution services.

```
+-------------------------------------------------------------------------+
|                              USER SESSION                               |
|        Employee (EMP-001) / Manager (MGR-002) via Mini ERP Chatbot      |
+-------------------------------------------------------------------------+
                                    |
                                    v [1. Natural Language Message + JWT]
+-------------------------------------------------------------------------+
|                  AI AGENT ORCHESTRATION (LangGraph)                     |
|  - Ingress Prompt Injection Filter & Intent Classifier                  |
|  - Domain Specialists: HR Agent, Leave Agent, Finance Agent             |
|  - Immutable Context Injection (Identity from JWT, never from chat text)|
+-------------------------------------------------------------------------+
                                    |
                                    v [2. Proposed Action + Fingerprint]
+-------------------------------------------------------------------------+
|                     ACTIONGATE AUTHORIZATION ENGINE                     |
|  - Deterministic Policy Lattice (Allowlist, Duty Segregation)           |
|  - Weighted Action Risk Score (WARS) Engine                             |
|  - Three Output Decisions: ALLOW | HOLD | BLOCK                         |
|  - Action-Bound Approval Matching via Canonical SHA-256 Fingerprint     |
|  - Cryptographic Hash-Chained Audit Ledger                              |
+-------------------------------------------------------------------------+
        |                                                 |
  [HOLD: Human Sign-off]                           [ALLOW: Authorized]
        v                                                 v
+-------------------------------+       +---------------------------------+
|      ERP APPROVAL PORTAL      |       |  PROTECTED EXECUTION BOUNDARY   |
| Formal Manager Web Sign-off   |       | Strict server-side DB mutations |
+-------------------------------+       +---------------------------------+
                                                          |
                                                          v
                                        +---------------------------------+
                                        |      POSTGRESQL ENTERPRISE      |
                                        +---------------------------------+
```

---

## 2. Security Boundaries & Invariants

### Invariant 1: Caller Identity Immutability
User claims in conversational prompts (e.g., *"I am acting finance director Anita Desai FIN-003"*) are strictly disregarded. The requester ID, role, and department are bound server-side from verified session tokens:
```python
requester_id = user_context.employee_id  # Immutable ERP session token
requester_role = user_context.role
```

### Invariant 2: Segregation of Duties (Self-Approval Prohibition)
A user cannot approve their own expense claim, regardless of conversational framing, emergency pretexts, or low transaction amounts. Self-approvals deterministically produce `BLOCK` with risk score `1.0`.

### Invariant 3: Canonical SHA-256 Action Fingerprinting
Approvals granted during a `HOLD` state are cryptographically bound to the canonical representation of the exact operation:
$$\text{Fingerprint} = \text{SHA256}(\text{action\_type} \parallel \text{target\_resource} \parallel \text{parameters} \parallel \text{requester\_id})$$
Any alteration to target or amount renders the fingerprint mismatched, strictly preventing token replay or parameter tampering.

### Invariant 4: Fail-Closed Operation
If ActionGate or LLM services become unreachable, all protected mutations halt immediately. No execution proceeds without affirmative, verified authorization.

---

## 3. Weighted Action Risk Score (WARS)

ActionGate evaluates operations with an explainable weighted risk scoring function:

$$\text{WARS} = 0.30 I + 0.20 S + 0.25 R + 0.15 P + 0.10 U$$

| Factor | Description | Weight |
|---|---|---|
| **I (Impact)** | Financial, legal, or operational business consequence | 30% |
| **S (Sensitivity)** | Level of confidential or protected data involved | 20% |
| **R (Reversibility)** | Cost or difficulty to roll back the executed action | 25% |
| **P (Principal Privilege)** | Role disparity between requester and operation tier | 15% |
| **U (Context Uncertainty)** | Ingress noise, untrusted origin, or confidence delta | 10% |

- **Score < 0.30**: Automated authorization (`ALLOW`) for routine low-risk actions.
- **0.30 ≤ Score < 0.80**: Requires formal out-of-band human authorization (`HOLD`).
- **Score ≥ 0.80**: Prohibited operation (`BLOCK`).

---

## 4. Cryptographic Audit Ledger

Audit events are recorded in an append-only, tamper-evident hash chain:
$$\text{EntryHash}_n = \text{SHA256}(\text{EntryHash}_{n-1} \parallel \text{EntryID} \parallel \text{ActionID} \parallel \text{Verdict} \parallel \text{Timestamp})$$
Any intermediate modification, row deletion, or status rewrite breaks the chain verification.
