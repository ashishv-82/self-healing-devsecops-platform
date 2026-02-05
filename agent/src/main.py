from fastapi import FastAPI, Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Self-Healing AI Agent")

# Prometheus Metrics
ALERTS_RECEIVED = Counter('agent_alerts_received_total', 'Total alerts received by the agent')
REMEDIATIONS_ATTEMPTED = Counter('agent_remediations_attempted_total', 'Total remediation attempts', ['action'])
REMEDIATIONS_SUCCESSFUL = Counter('agent_remediations_successful_total', 'Total successful remediations', ['action'])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-agent"}

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

from src.graph.graph import create_graph

# Initialize Graph
graph = create_graph()

@app.get("/")
async def root():
    return {"message": "Self-Healing AI Agent is running"}

@app.post("/webhook")
async def receive_alert(alert: dict):
    print(f"📥 Webhook: Received alert: {alert}")
    ALERTS_RECEIVED.inc()
    
    # Transform Alertmanager payload to AgentState
    alert_info = {
        "alert_name": alert.get("groupLabels", {}).get("alertname", "Unknown"),
        "severity": alert.get("commonLabels", {}).get("severity", "unknown"),
        "service": alert.get("commonLabels", {}).get("instance", "unknown"),
        "details": alert
    }
    
    initial_state = {"alert": alert_info}
    
    # Execute Graph
    print("🚀 invoking LangGraph...")
    result = graph.invoke(initial_state)
    
    # Track remediation metrics
    action = result.get("plan", {}).get("action", "unknown")
    REMEDIATIONS_ATTEMPTED.labels(action=action).inc()
    if "Success" in result.get("execution_result", ""):
        REMEDIATIONS_SUCCESSFUL.labels(action=action).inc()
    
    print(f"✅ Execution Complete. Result: {result.get('execution_result')}")
    return {"status": "processed", "result": result.get("execution_result")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

