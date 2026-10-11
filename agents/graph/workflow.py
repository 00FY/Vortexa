from typing import Optional
from langgraph.graph import StateGraph, END
from agents.graph.state import ChatState
from agents.graph.nodes import (
    authenticate_and_validate_context,
    classify_intent_and_route,
    invoke_specialized_agent,
    validate_action_allowlist,
    evaluate_with_actiongate,
    execute_or_handle_decision,
    synthesize_final_response,
)
from agents.gate_client.actiongate_client import ActionGateClient
from agents.gate_client.erp_client import ERPClient

def create_orchestrator_graph(
    actiongate_client: Optional[ActionGateClient] = None,
    erp_client: Optional[ERPClient] = None
):
    workflow = StateGraph(ChatState)

    workflow.add_node("authenticate", authenticate_and_validate_context)
    workflow.add_node("classify_intent", classify_intent_and_route)
    workflow.add_node("invoke_agent", invoke_specialized_agent)
    workflow.add_node("validate_action", validate_action_allowlist)
    
    def evaluate_node(state: ChatState):
        return evaluate_with_actiongate(state, actiongate_client=actiongate_client)

    def execute_node(state: ChatState):
        return execute_or_handle_decision(state, erp_client=erp_client)

    workflow.add_node("evaluate_actiongate", evaluate_node)
    workflow.add_node("execute_or_handle", execute_node)
    workflow.add_node("synthesize", synthesize_final_response)

    def check_auth(state: ChatState) -> str:
        if state.get("validation_error"):
            return "synthesize"
        return "classify_intent"

    def check_intent(state: ChatState) -> str:
        if state.get("validation_error") or state.get("final_response"):
            return "synthesize"
        return "invoke_agent"

    def check_agent(state: ChatState) -> str:
        if state.get("clarification_message") or state.get("validation_error"):
            return "synthesize"
        return "validate_action"

    def check_action(state: ChatState) -> str:
        if state.get("validation_error"):
            return "synthesize"
        return "evaluate_actiongate"

    def check_actiongate(state: ChatState) -> str:
        if state.get("outage_error") or state.get("final_response"):
            return "synthesize"
        return "execute_or_handle"

    workflow.set_entry_point("authenticate")
    workflow.add_conditional_edges("authenticate", check_auth, {"synthesize": "synthesize", "classify_intent": "classify_intent"})
    workflow.add_conditional_edges("classify_intent", check_intent, {"synthesize": "synthesize", "invoke_agent": "invoke_agent"})
    workflow.add_conditional_edges("invoke_agent", check_agent, {"synthesize": "synthesize", "validate_action": "validate_action"})
    workflow.add_conditional_edges("validate_action", check_action, {"synthesize": "synthesize", "evaluate_actiongate": "evaluate_actiongate"})
    workflow.add_conditional_edges("evaluate_actiongate", check_actiongate, {"synthesize": "synthesize", "execute_or_handle": "execute_or_handle"})
    workflow.add_edge("execute_or_handle", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()
