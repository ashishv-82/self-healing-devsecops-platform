import pytest
from src.graph.nodes import analyst_node, auditor_node, decision_node, remediation_node, verification_node

# Mock data for testing
MOCK_STATE = {
    "alert": {
        "alert_name": "TestAlert",
        "service": "frontend-test",
        "severity": "critical",
        "details": {}
    }
}

def test_analyst_node_returns_logs_and_analysis():
    """Analyst node should return logs and analysis keys."""
    result = analyst_node(MOCK_STATE)
    assert "logs" in result
    assert "analysis" in result
    assert isinstance(result["logs"], list)
    assert isinstance(result["analysis"], str)

def test_auditor_node_returns_commits():
    """Auditor node should return recent_commits key."""
    result = auditor_node(MOCK_STATE)
    assert "recent_commits" in result
    assert isinstance(result["recent_commits"], list)

def test_decision_node_restart_on_network_issue():
    """Decision node should recommend restart for connection issues."""
    state = {"analysis": "Error: Connection refused to database."}
    result = decision_node(state)
    
    assert "plan" in result
    assert result["plan"]["action"] == "restart_service"
    assert result["plan"]["confidence"] >= 0.9

def test_decision_circuit_breaker():
    """Decision node should escalate after too many retries."""
    state = {"analysis": "Some error", "retry_count": 5}
    result = decision_node(state)
    
    assert result["plan"]["action"] == "escalate"
    assert result["plan"]["reasoning"] == "Circuit breaker tripped."

def test_remediation_node_requires_plan():
    """Remediation node should error if no plan provided."""
    state = {"plan": None}
    result = remediation_node(state)
    
    assert "error" in result

def test_verification_node_success():
    """Verification node should report success for healthy system."""
    state = {}
    result = verification_node(state)
    
    assert "execution_result" in result
    assert "Success" in result["execution_result"]
