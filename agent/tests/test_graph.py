import pytest
from src.graph.graph import create_graph

# Mock dependencies if strictly unit testing, 
# but for this foundational test we check graph structure/execution.

def test_graph_creation():
    """Verify the graph compiles successfully."""
    graph = create_graph()
    assert graph is not None

def test_analyst_node_output():
    """Verify detailed analysis flow (mocked)"""
    from src.graph.nodes import analyst_node
    
    state = {
        "alert": {
            "alert_name": "TestAlert", 
            "service": "frontend-service",
            "severity": "critical",
            "details": {}
        }
    }
    
    result = analyst_node(state)
    assert "logs" in result
    assert "analysis" in result
    assert result["analysis"] is not None

def test_decision_logic_restart():
    """Verify decision logic recommends restart for network issues"""
    from src.graph.nodes import decision_node
    
    state = {
        "analysis": "Error: Connection refused to database."
    }
    
    result = decision_node(state)
    plan = result["plan"]
    
    assert plan["action"] == "restart_service"
    assert plan["confidence"] >= 0.9
