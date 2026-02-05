import pytest
from unittest.mock import patch, MagicMock

# Test CloudWatch Client
def test_filter_log_events_handles_missing_log_group():
    """CloudWatch client should gracefully handle missing log groups."""
    from src.tools.cloudwatch_client import filter_log_events
    
    # This will attempt to connect to LocalStack and likely fail
    # The function should return an empty list, not crash
    result = filter_log_events("/ecs/non-existent-log-group")
    assert isinstance(result, list)

# Test ECS Client
def test_restart_service_structure():
    """ECS client restart_service function should exist and be callable."""
    from src.tools.ecs_client import restart_service
    
    # Just test that the function exists and has correct signature
    assert callable(restart_service)
    
def test_update_desired_count_structure():
    """ECS client update_desired_count function should exist and be callable."""
    from src.tools.ecs_client import update_desired_count
    
    assert callable(update_desired_count)

# Test GitHub Client
def test_get_recent_commits_mock_fallback():
    """GitHub client should return mock data when no token is set."""
    import os
    original_token = os.environ.get("GITHUB_TOKEN", "")
    os.environ["GITHUB_TOKEN"] = ""
    
    from src.tools.github_client import get_recent_commits
    result = get_recent_commits("test-service")
    
    os.environ["GITHUB_TOKEN"] = original_token
    
    assert isinstance(result, list)
