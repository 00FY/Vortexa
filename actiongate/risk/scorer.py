"""Weighted Action Risk Score (WARS) Engine.

Formula:
    WARS = 0.30*I + 0.20*S + 0.25*R + 0.15*P + 0.10*U

Where:
- I (Impact): Financial or operational business impact (0.0 to 1.0)
- S (Sensitivity): Confidentiality of affected entity/records (0.0 to 1.0)
- R (Reversibility): Difficulty of rolling back the mutation (0.0 to 1.0)
- P (Permission): Risk associated with requester's role level (0.0 to 1.0)
- U (Uncertainty): Missing provenance or unverified inputs (0.0 to 1.0)
"""

from typing import Dict, Any, Tuple
from actiongate.types import RiskLevel


class WeightedActionRiskScorer:
    WEIGHT_IMPACT = 0.30
    WEIGHT_SENSITIVITY = 0.20
    WEIGHT_REVERSIBILITY = 0.25
    WEIGHT_PERMISSION = 0.15
    WEIGHT_UNCERTAINTY = 0.10

    def compute_risk(self, request_data: Dict[str, Any]) -> Tuple[float, RiskLevel, Dict[str, float]]:
        """
        Calculates explainable risk score normalized between 0.0 and 1.0.
        Returns: (total_score, risk_tier, factor_breakdown)
        """
        action_type = request_data.get("action_type", "")
        params = request_data.get("parameters", {})
        requester_role = request_data.get("requester_role", "EMPLOYEE").upper()
        context_sources = request_data.get("context_sources", [])

        # 1. Impact (I) - Based on financial amount or record count
        amount = float(params.get("amount", 0.0))
        if amount <= 0:
            record_count = int(params.get("record_count", 0))
            if record_count <= 25:
                i_factor = 0.1
            elif record_count <= 500:
                i_factor = 0.5
            else:
                i_factor = 0.95
        else:
            if amount <= 5000.0:
                i_factor = 0.10
            elif amount <= 25000.0:
                i_factor = 0.35
            elif amount <= 100000.0:
                i_factor = 0.65
            else:
                i_factor = 1.0

        # 2. Sensitivity (S) - Based on affected entity
        target = request_data.get("target_resource", "").lower()
        if any(term in target or term in action_type for term in ["salary", "ssn", "credentials", "banking", "payroll"]):
            s_factor = 0.95
        elif any(term in target or term in action_type for term in ["expense", "supplier", "kyc"]):
            s_factor = 0.60
        elif any(term in target or term in action_type for term in ["leave"]):
            s_factor = 0.20
        else:
            s_factor = 0.10

        # 3. Reversibility (R)
        if "delete" in action_type or "payout" in action_type or "wire" in action_type or amount > 50000.0:
            r_factor = 0.85
        elif "approve" in action_type or "update" in action_type:
            r_factor = 0.50
        else:
            r_factor = 0.15

        # 4. Permission (P)
        if requester_role in ["ADMIN", "FINANCE_ADMIN", "DIRECTOR"]:
            p_factor = 0.20
        elif requester_role == "MANAGER":
            p_factor = 0.40
        else:
            p_factor = 0.70

        # 5. Uncertainty (U) - Untrusted provenance increases uncertainty
        has_untrusted_source = any(not s.get("trusted", True) for s in context_sources)
        if has_untrusted_source:
            u_factor = 0.90
        elif not context_sources:
            u_factor = 0.40
        else:
            u_factor = 0.10

        total_score = round(
            (self.WEIGHT_IMPACT * i_factor) +
            (self.WEIGHT_SENSITIVITY * s_factor) +
            (self.WEIGHT_REVERSIBILITY * r_factor) +
            (self.WEIGHT_PERMISSION * p_factor) +
            (self.WEIGHT_UNCERTAINTY * u_factor),
            4
        )
        total_score = max(0.0, min(1.0, total_score))

        if total_score < 0.30:
            tier = RiskLevel.LOW
        elif total_score < 0.60:
            tier = RiskLevel.MEDIUM
        elif total_score < 0.85:
            tier = RiskLevel.HIGH
        else:
            tier = RiskLevel.CRITICAL

        breakdown = {
            "impact": i_factor,
            "sensitivity": s_factor,
            "reversibility": r_factor,
            "permission": p_factor,
            "uncertainty": u_factor,
        }
        return total_score, tier, breakdown
