from .state import AgentState, RemediationPlan
from src.tools.cloudwatch_client import filter_log_events
from src.tools.github_client import get_recent_commits, create_revert_pr
from src.tools.ecs_client import restart_service, update_desired_count
import random
import os

# ============================================================================
# PHASE 3: Real Tool Integration
# ============================================================================

def analyst_node(state: AgentState) -> AgentState:
    """
    Analyzes the alert and logs to determine the root cause.
    Implements graceful degradation if CloudWatch is unavailable.
    """
    alert_name = state['alert']['alert_name']
    service_name = state['alert']['service']
    print(f"🕵️ Analyst Node: Analyzing alert '{alert_name}' for service '{service_name}'...")
    
    # 1. Derive Log Group Name from Service Name
    log_group = f"/ecs/{service_name}"
    if service_name == "localhost:8080":  # Testing override
        log_group = "/ecs/self-healing-devsecops-frontend-dev"

    print(f"   🔍 Querying CloudWatch Logs: {log_group}")
    
    # Graceful Degradation: If CloudWatch fails, continue with partial data
    try:
        logs = filter_log_events(log_group)
    except Exception as e:
        print(f"⚠️ Graceful Degradation: CloudWatch unavailable ({e}). Proceeding without logs.")
        logs = []
    
    # 2. Heuristic Analysis (Placeholder for LLM)
    analysis = "Unknown Issue"
    if not logs:
        analysis = "No logs found. Possible health check failure or network issue."
    else:
        # Simple keyword matching for V1
        error_logs = [l for l in logs if "Error" in l or "Exception" in l]
        if error_logs:
            analysis = f"Found {len(error_logs)} error logs. Top error: {error_logs[0][:100]}..."
        else:
            analysis = "Logs found but no explicit errors detected."
    
    return {"logs": logs, "analysis": analysis}

def auditor_node(state: AgentState) -> AgentState:
    """
    Checks recent commits to see if a code change caused the issue.
    Implements graceful degradation if GitHub is unavailable.
    """
    service_name = state['alert']['service']
    print(f"👮 Auditor Node: Checking recent commits for {service_name}...")
    
    # Graceful Degradation: If GitHub fails, continue without commit data
    try:
        commits = get_recent_commits(service_name)
    except Exception as e:
        print(f"⚠️ Graceful Degradation: GitHub unavailable ({e}). Proceeding without commit data.")
        commits = []
    
    return {"recent_commits": commits}

def verification_node(state: AgentState) -> AgentState:
    """
    Verifies if the remediation was successful.
    """
    print("✅ Verification Node: Checking system health after remediation...")
    
    # For now, we assume if we reached here without crash, it's tentatively okay.
    # Ideally, Query Prometheus again.
    healthy = True
    
    if healthy:
        return {"execution_result": "Success: System recovered."}
    else:
        return {"execution_result": "Failure: System still unhealthy.", "retry_count": state.get("retry_count", 0) + 1}

def decision_node(state: AgentState) -> AgentState:
    analysis = state.get('analysis')
    print(f"⚖️ Decision Node: (Analysis: {analysis})")
    
    # Circuit Breaker Logic
    retry_count = state.get("retry_count", 0)
    if retry_count > 2:
        print("⛔ Circuit Breaker: Too many retries. Escalating.")
        return {"plan": {"action": "escalate", "reasoning": "Circuit breaker tripped.", "confidence": 1.0}}

    # Heuristic Decision Logic (Placeholder for LLM)
    # If "Connection refused" or "Unhealthy", RESTART.
    # If "High CPU" or capacity issues, SCALE_UP.
    # If code error, REVERT or Escalate.
    
    action = "escalate"
    confidence = 0.5
    
    if "Connection refused" in analysis or "Network" in analysis:
        action = "restart_service"
        confidence = 0.9
    elif "High CPU" in analysis or "capacity" in analysis.lower() or "overload" in analysis.lower():
        action = "scale_up"
        confidence = 0.85
    elif "NullPointer" in analysis or "TypeError" in analysis or "undefined" in analysis.lower():
        # Code error - likely caused by recent deploy
        action = "revert_commit"
        confidence = 0.75
    elif "test" in analysis.lower() or "simulated" in analysis.lower():
         action = "restart_service"
         confidence = 0.95
    else:
        # Default fallback
        action = "restart_service" 
        confidence = 0.8
        
    print(f"   👉 Decision: {action} (Confidence: {confidence})")

    if confidence < 0.7:
        print(f"⚠️ Low Confidence ({confidence}). Escalating.")
        return {"plan": {"action": "escalate", "reasoning": "Low confidence in autonomous fix.", "confidence": confidence}}
    
    plan: RemediationPlan = {
        "action": action,
        "reasoning": f"Based on analysis: {analysis}",
        "confidence": confidence
    }
    
    return {"plan": plan}

def remediation_node(state: AgentState) -> AgentState:
    """
    Executes the chosen remediation plan.
    Feature flags control which actions are enabled.
    """
    plan = state['plan']
    if not plan:
        return {"error": "No plan provided."}
        
    action = plan['action']
    
    # Feature Flags - Control which autonomous actions are allowed
    ALLOWED_ACTIONS = {
        "restart_service": os.getenv("ENABLE_RESTART", "true").lower() == "true",
        "scale_up": os.getenv("ENABLE_SCALE_UP", "true").lower() == "true",
        "revert_commit": os.getenv("ENABLE_REVERT", "false").lower() == "true",  # Disabled by default
        "escalate": True  # Always allowed
    }
    
    if not ALLOWED_ACTIONS.get(action, False):
        print(f"⛔ Feature Flag: Action '{action}' is disabled. Escalating.")
        return {"execution_result": f"Action '{action}' is disabled by feature flag. Escalated to human operator."}
    
    print(f"🛠️ Remediation Node: Executing {action}...")
    
    execution_result = "Failed"
    
    if action == "restart_service":
        # Extract cluster/service from Alert or Config
        cluster = os.getenv("ECS_CLUSTER", "devsecops-cluster-dev")
        service = os.getenv("ECS_SERVICE", "frontend-app-dev")
        
        success = restart_service(cluster, service)
        if success:
             execution_result = "Success: Service restarted."
        else:
             execution_result = "Failure: Could not restart service."
    
    elif action == "scale_up":
        # Scale up the service to handle increased load
        cluster = os.getenv("ECS_CLUSTER", "devsecops-cluster-dev")
        service = os.getenv("ECS_SERVICE", "frontend-app-dev")
        current_count = 1  # Would fetch from ECS in production
        new_count = current_count + 1
        
        success = update_desired_count(cluster, service, new_count)
        if success:
             execution_result = f"Success: Scaled service to {new_count} tasks."
        else:
             execution_result = "Failure: Could not scale service."
    
    elif action == "revert_commit":
        # Revert a recent commit that may have caused the issue
        recent_commits = state.get("recent_commits", [])
        if recent_commits:
            commit_to_revert = recent_commits[0].get("sha", "")
            reason = state.get("analysis", "Unknown issue detected")
            
            result = create_revert_pr(commit_to_revert, reason)
            if result.get("success"):
                execution_result = f"Success: {result.get('message')}. PR: {result.get('pr_url')}"
            else:
                execution_result = f"Failure: Could not create revert PR. {result.get('message')}"
        else:
            execution_result = "Failure: No recent commits found to revert."
    
    elif action == "escalate":
        execution_result = "Escalated to human operator."
    
    return {"execution_result": execution_result}
