from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.graph.nodes import analyst_node, auditor_node, decision_node, remediation_node, verification_node

def create_graph():
    workflow = StateGraph(AgentState)

    # Define Nodes
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("auditor", auditor_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("remediation", remediation_node)
    workflow.add_node("verification", verification_node)

    # Define Edges
    # Parallel execution: Entry -> (Analyst, Auditor) -> Decision
    workflow.set_entry_point("analyst")
    workflow.add_edge("analyst", "auditor") # Sequential for simplicity in V1 for now (Analyst -> Auditor -> Decision)
    workflow.add_edge("auditor", "decision")
    
    workflow.add_edge("decision", "remediation")
    workflow.add_edge("remediation", "verification")
    
    # In V2, we add conditional edge: retry if verification fails
    workflow.add_edge("verification", END)

    return workflow.compile()
