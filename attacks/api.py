"""
attacks/api.py
--------------
FastAPI router providing REST endpoints for the Attack Lab UI.
Allows the frontend to query the 6 attack scenarios, trigger live runs,
and test custom freeform adversarial prompts against the LangGraph orchestrator.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from attacks.scenarios import (
    get_attack_scenarios,
    execute_attack_scenario,
    get_default_users,
)
from agents.graph.workflow import create_orchestrator_graph
from agents.gate_client.mocks import MockERP, MockActionGate
from agents.gate_client.erp_client import ERPClient
from agents.gate_client.actiongate_client import ActionGateClient

router = APIRouter(prefix="/attacks", tags=["Attack Lab"])


class FreeformPromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Adversarial prompt text to test")
    role: str = Field("EMPLOYEE", description="EMPLOYEE or MANAGER")


@router.get("/scenarios")
def list_scenarios():
    """Returns catalog of the 6 core attack scenarios."""
    scenarios = get_attack_scenarios()
    return [
        {
            "id": sc.id,
            "name": sc.name,
            "category": sc.category,
            "description": sc.description,
            "attacker_intent": sc.attacker_intent,
            "expected_outcome": sc.expected_outcome,
            "adversarial_technique": sc.adversarial_technique,
            "actiongate_defense": sc.actiongate_defense_mechanism,
            "steps_count": len(sc.steps),
            "sample_prompt": sc.steps[0].user_prompt,
        }
        for sc in scenarios
    ]


@router.post("/run/{scenario_id}")
def run_scenario(scenario_id: str):
    """Executes a specific attack scenario against the orchestrator and returns full tracing."""
    scenarios = {sc.id: sc for sc in get_attack_scenarios()}
    if scenario_id not in scenarios:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    
    result = execute_attack_scenario(scenarios[scenario_id])
    return result


@router.post("/run-all")
def run_all_scenarios():
    """Executes all 6 attack scenarios and returns quantitative summary."""
    scenarios = get_attack_scenarios()
    results = [execute_attack_scenario(sc) for sc in scenarios]
    total = len(results)
    defended = sum(1 for r in results if r["defended"])
    erp_unmodified = sum(1 for r in results if not r["erp_state_modified"])

    return {
        "total_scenarios": total,
        "defended_count": defended,
        "defense_rate": defended / total if total else 0.0,
        "erp_unmodified_count": erp_unmodified,
        "results": results,
    }


@router.post("/freeform")
def test_freeform_prompt(payload: FreeformPromptRequest):
    """
    Evaluates a freeform adversarial prompt submitted by judges or presenters.
    Shows the step-by-step chain of Agent Interpretation -> ActionGate Evaluation -> Decision.
    """
    mock_erp = MockERP()
    mock_actiongate = MockActionGate(erp_backend=mock_erp)
    erp_client = ERPClient(mock_instance=mock_erp)
    actiongate_client = ActionGateClient(mock_instance=mock_actiongate)
    orchestrator = create_orchestrator_graph(actiongate_client=actiongate_client, erp_client=erp_client)

    emp_user, mgr_user = get_default_users()
    user_ctx = mgr_user if payload.role.upper() == "MANAGER" else emp_user

    initial_claims = {k: v.get("status") for k, v in mock_erp.expenses.items()}

    output_state = orchestrator.invoke({
        "user_message": payload.prompt,
        "user_context": user_ctx,
    })

    dec_obj = output_state.get("actiongate_decision")
    prop_action = output_state.get("proposed_action")

    final_claims = {k: v.get("status") for k, v in mock_erp.expenses.items()}
    erp_modified = (initial_claims != final_claims)

    dec_str = dec_obj.decision.value if dec_obj else "NONE"
    risk_val = dec_obj.risk_score if dec_obj else (1.0 if output_state.get("status") == "BLOCKED" else 0.0)

    defended = (
        not erp_modified and
        (dec_str in ["BLOCK", "HOLD"] or output_state.get("status") in ["BLOCKED", "HELD", "NEEDS_CLARIFICATION"])
    )

    return {
        "prompt": payload.prompt,
        "role_tested": user_ctx.role.value,
        "status": output_state.get("status"),
        "agent_response": output_state.get("final_response"),
        "proposed_action": {
            "action_type": prop_action.action_type.value if prop_action else None,
            "target_resource": prop_action.target_resource if prop_action else None,
            "requester_id": prop_action.requester_id if prop_action else None,
            "fingerprint": prop_action.action_fingerprint if prop_action else None,
        } if prop_action else None,
        "actiongate_decision": {
            "decision": dec_str,
            "risk_score": risk_val,
            "reasons": dec_obj.reasons if dec_obj else ["Blocked by Ingress Security Filter"],
        } if dec_obj else None,
        "defended": defended,
        "erp_state_modified": erp_modified,
    }
