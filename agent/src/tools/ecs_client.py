import boto3
import os
from botocore.exceptions import ClientError

# Connection setup
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
LOCAL_DEV = os.getenv("LOCAL_DEV", "false").lower() == "true"
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", None)

def get_ecs_client():
    if LOCAL_DEV:
        return boto3.client(
            "ecs",
            region_name=AWS_REGION,
            endpoint_url=AWS_ENDPOINT_URL,
            aws_access_key_id="test",
            aws_secret_access_key="test"
        )
    return boto3.client("ecs", region_name=AWS_REGION)

def restart_service(cluster_name: str, service_name: str) -> bool:
    """
    Restarts an ECS service by forcing a new deployment.
    """
    client = get_ecs_client()
    try:
        print(f"🔄 Restarting ECS Service: {service_name} in cluster {cluster_name}...")
        response = client.update_service(
            cluster=cluster_name,
            service=service_name,
            forceNewDeployment=True
        )
        # Check if status is correct
        status = response.get('service', {}).get('status')
        print(f"✅ Service update initiated. Status: {status}")
        return True
    except ClientError as e:
        print(f"❌ Failed to restart service: {e}")
        return False

def update_desired_count(cluster_name: str, service_name: str, desired_count: int) -> bool:
    """
    Updates the desired count of tasks for an ECS service.
    """
    client = get_ecs_client()
    try:
        print(f"⚖️  Scaling ECS Service: {service_name} to {desired_count} tasks...")
        response = client.update_service(
            cluster=cluster_name,
            service=service_name,
            desiredCount=desired_count
        )
        print(f"✅ Scale update initiated.")
        return True
    except ClientError as e:
        print(f"❌ Failed to update desired count: {e}")
        return False

if __name__ == "__main__":
    # Test execution
    # Note: This will likely fail in LocalStack if the service wasn't created via Terraform/CloudFormation with the exact name.
    # But it proves connection.
    restart_service("devsecops-cluster-dev", "frontend-app-dev")
