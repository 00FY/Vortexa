"""Policy hook integration point for ActionGate.

Every future business write must call this hook before mutation.
This hook does not replace authentication, role checks, self-approval
prevention, or resource-level authorization.
"""


def policy_check(actor, action, resource, resource_id, params=None) -> None:
    # This is the integration point for ActionGate policy checks.
    # For now it is a no-op; later it will delegate to ActionGate.
    pass
