import boto3
import os
import time
from typing import List, Dict, Any

# Connection setup
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
LOCAL_DEV = os.getenv("LOCAL_DEV", "false").lower() == "true"
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", None)

def get_cw_client():
    if LOCAL_DEV:
        return boto3.client(
            "logs",
            region_name=AWS_REGION,
            endpoint_url=AWS_ENDPOINT_URL,
            aws_access_key_id="test",
            aws_secret_access_key="test"
        )
    return boto3.client("logs", region_name=AWS_REGION)

def filter_log_events(log_group_name: str, filter_pattern: str = "ERROR", start_time_minutes: int = 15) -> List[str]:
    """
    Fetches log events from CloudWatch Logs that match a filter pattern.
    
    Args:
        log_group_name: The name of the log group (e.g., /ecs/frontend-app-dev)
        filter_pattern: The pattern to search for (e.g., "Exception")
        start_time_minutes: How many minutes back to search
        
    Returns:
        List of log messages found.
    """
    client = get_cw_client()
    
    # CloudWatch expects start_time in milliseconds
    start_time = int((time.time() - (start_time_minutes * 60)) * 1000)
    
    try:
        response = client.filter_log_events(
            logGroupName=log_group_name,
            filterPattern=filter_pattern,
            startTime=start_time,
            limit=50
        )
        
        events = response.get('events', [])
        messages = [event['message'] for event in events]
        return messages

    except client.exceptions.ResourceNotFoundException:
        print(f"❌ Log group {log_group_name} not found.")
        return []
    except Exception as e:
        print(f"❌ Error fetching logs: {e}")
        return []

if __name__ == "__main__":
    # Test execution
    print("Testing connection...")
    logs = filter_log_events("/ecs/self-healing-devsecops-frontend-dev")
    print(f"Found {len(logs)} logs.")
