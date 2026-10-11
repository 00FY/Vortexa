import hashlib
import json
from typing import Dict, Any

def calculate_action_fingerprint(
    action_type: str,
    target_resource: str,
    parameters: Dict[str, Any],
    requester_id: str
) -> str:
    """
    Computes a deterministic cryptographic SHA-256 fingerprint for an exact proposed action.
    Any tampering with action type, parameters, target resource, or requester identity produces
    a completely different hash, ensuring immutable action provenance.
    """
    canonical_payload = {
        "action_type": action_type.strip(),
        "target_resource": target_resource.strip(),
        "requester_id": requester_id.strip(),
        "parameters": parameters,
    }
    encoded = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
