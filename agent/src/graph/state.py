from typing import TypedDict, List, Optional, Dict, Any, Literal

class AlertInfo(TypedDict):
    alert_name: str
    severity: str
    service: str
    details: Dict[str, Any]

class RemediationPlan(TypedDict):
    action: Literal["restart_service", "scale_up", "revert_commit", "escalate"]
    reasoning: str
    confidence: float

class AgentState(TypedDict):
    # INPUT
    alert: AlertInfo
    
    # MEMORY / CONTEXT
    logs: Optional[List[str]]
    recent_commits: Optional[List[Dict[str, Any]]]
    
    # OUTPUTS
    analysis: Optional[str]      # Root cause analysis from LLM
    plan: Optional[RemediationPlan]
    execution_result: Optional[str]
    
    # CONTROL FLOW
    retry_count: int
    error: Optional[str]
