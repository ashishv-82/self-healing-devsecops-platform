import pytest
import sys
import os

# Add agent/src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def mock_alert():
    """Standard mock alert for testing."""
    return {
        "alert": {
            "alert_name": "TestAlert",
            "service": "frontend-test",
            "severity": "critical",
            "details": {}
        }
    }

@pytest.fixture
def mock_state_with_analysis():
    """State with completed analysis for decision testing."""
    return {
        "alert": {
            "alert_name": "TestAlert",
            "service": "frontend-test",
            "severity": "critical",
            "details": {}
        },
        "logs": ["Error: Connection refused"],
        "analysis": "Connection refused error detected."
    }
