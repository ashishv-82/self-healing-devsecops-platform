# Project Tasks: Self-Healing DevSecOps Platform

## Phase 1: Foundation (Infrastructure & Baseline)

### Repository & Local Environment
- [ ] Initialize git repository with `.gitignore` and `README.md`
- [ ] Create folder structure:
  - [ ] `terraform/modules/` (networking, ecs-cluster, iam, observability)
  - [ ] `terraform/environments/` (dev, prod)
  - [ ] `agent/src/` (main.py, graph/, tools/, mcp/)
  - [ ] `agent/tests/`
  - [ ] `.github/workflows/`
  - [ ] `astronomy-shop/kubernetes/` (reference)
  - [ ] `astronomy-shop/ecs-taskdefs/`
  - [ ] `chaos/experiments/`
  - [ ] `chaos/validation/`
  - [ ] `dashboards/grafana/`
  - [ ] `dashboards/prometheus/`
  - [ ] `docs/runbooks/`
  - [ ] `docs/adr/`
- [ ] Create `docker-compose.local.yml` with Prometheus, Grafana, and Astronomy Shop
- [ ] Create `agent/Dockerfile`
- [ ] Create `agent/requirements.txt`
- [ ] Verify local stack startup and inter-container networking
- [ ] (Optional) Add LocalStack service for AWS API mocking

### Terraform Infrastructure
- [ ] **State Management**: Create S3 bucket + DynamoDB table for state locking
- [ ] **Cost Management**: Configure AWS Budgets (50%/80% alerts) and Cost Allocation Tags
- [ ] **Networking**: Define VPC, Public/Private Subnets, IGW, Route Tables, Security Groups
- [ ] **VPC Endpoints**: Configure endpoints for ECR API, ECR DKR, S3 (gateway), CloudWatch Logs
- [ ] **IAM**: Create ECS Task Execution Role
- [ ] **IAM**: Create Agent Runtime Role (least-privilege: ECS, CloudWatch, Bedrock)
- [ ] **ECS Cluster**: Provision Fargate Cluster
- [ ] **ALB**: Provision Application Load Balancer with path-based routing
- [ ] Create `terraform/environments/dev/terraform.tfvars`
- [ ] Create `terraform/environments/prod/terraform.tfvars` (for demo mode)

### CI/CD Setup (GitHub Actions)
- [ ] Configure AWS OIDC provider for keyless authentication
- [ ] Create `terraform-apply.yml` (Plan on PR, Apply on merge to main)
- [ ] Create `docker-build.yml` (Build agent image, push to ECR)
- [ ] Create `ecs-deploy.yml` (Trigger ECS service update on new image)
- [ ] Create `scheduled-infra.yml` (Scale to 0 at night, scale up in morning)
- [ ] Create `dashboard-sync.yml` (Push Grafana JSON to AWS)

### Observability & Baseline Deployment
- [ ] Containerize simplified Astronomy Shop services
- [ ] Create ECS Task Definitions for Astronomy Shop (ARM64, minimal resources)
- [ ] Deploy Astronomy Shop to ECS via Terraform
- [ ] **Prometheus**: Deploy self-hosted Prometheus on ECS
- [ ] **Grafana**: Deploy Grafana on ECS with provisioning volume
- [ ] **CloudWatch**: Verify ECS log driver configuration and log group creation

---

## Phase 2: Detection (Observability & Chaos)

### Observability Configuration
- [ ] Create `dashboards/prometheus/prometheus.yml` (scrape config for ECS)
- [ ] Create `dashboards/prometheus/alerting-rules.yml`
- [ ] Create Alertmanager configuration (webhook to agent)
- [ ] Create `dashboards/grafana/infra-overview.json`
- [ ] Create `dashboards/grafana/agent-activity.json`
- [ ] Test alerts locally (trigger fake metric spike)

### Webhook & Signaling
- [ ] Create FastAPI `agent/src/main.py` webhook receiver skeleton
- [ ] Add rate limiting middleware to webhook endpoint
- [ ] Configure Alertmanager to POST to FastAPI on alert
- [ ] Validate end-to-end: Metric spike → Alertmanager → Webhook → 200 OK

### Chaos Engineering (Foundation)
- [ ] Install Chaos Toolkit locally
- [ ] Create `chaos/experiments/container-crash.yaml`
- [ ] Create `chaos/experiments/network-latency.yaml`
- [ ] Create `chaos/experiments/cpu-stress.yaml`
- [ ] Create `chaos/validation/recovery-checks.py`
- [ ] **AWS FIS**: Define FIS experiment templates in Terraform
- [ ] Create `fis-experiment.yml` workflow to trigger FIS from GitHub Actions

---

## Phase 3: AI Agent (The "Brain")

### Core Logic (LangGraph)
- [ ] Set up LangGraph project structure in `agent/src/graph/`
- [ ] Create `agent/src/graph/state.py` (State schema: AlertInfo, Analysis, Plan)
- [ ] Create `agent/src/graph/nodes.py`:
  - [ ] Implement `analyst_node` (Query CloudWatch, identify error patterns)
  - [ ] Implement `auditor_node` (Query GitHub for recent commits)
  - [ ] Implement `decision_node` (Route: InfraFix vs CodeFix vs Escalate)
  - [ ] Implement `remediation_node` (Execute fix action)
  - [ ] Implement `verification_node` (Check Prometheus after fix)
- [ ] Create `agent/src/graph/edges.py` (State transitions, conditional routing)
- [ ] Implement LLM confidence thresholds (reject low-confidence decisions)
- [ ] Implement circuit breaker (max retries, cooldown period)

### Tool Implementation
- [ ] Create `agent/src/tools/cloudwatch_client.py` (filter_log_events)
- [ ] Create `agent/src/tools/github_client.py` (get_commits, create_pull_request)
- [ ] Create `agent/src/tools/ecs_client.py` (restart_service, update_desired_count)
- [ ] Wire tools into LangGraph nodes via tool bindings

### MCP Server (Optional Enhancement)
- [ ] Create `agent/src/mcp/server.py` (MCP protocol handler)
- [ ] Expose agent tools via MCP for external AI integration

### Integration & Deployment
- [ ] Write unit tests in `agent/tests/`
- [ ] Containerize Agent (finalize Dockerfile)
- [ ] Push Agent image to ECR
- [ ] Create ECS Task Definition for Agent
- [ ] Grant Agent IAM permissions (ECS, CloudWatch Logs, Bedrock/OpenAI)
- [ ] Deploy Agent to ECS
- [ ] Verify Agent receives webhook and queries CloudWatch in production

---

## Phase 4: Closed-Loop (Remediation & Verification)

### Remediation Workflows
- [ ] Implement "Restart" remediation (ECS UpdateService force new deployment)
- [ ] Implement "Scale-Up" remediation (increase desired count)
- [ ] Implement "Revert Commit" remediation (GitHub PR creation)
- [ ] Implement feature flags to enable/disable autonomous actions
- [ ] Implement graceful degradation (escalate to human if AI fails)
- [ ] Create `agent-pr.yml` workflow (auto-merge agent PRs if tests pass)

### Testing & Validation
- [ ] Run full self-healing loop: Chaos → Alert → Agent → Fix → Recovery
- [ ] Measure and record MTTR (Mean Time To Recovery)
- [ ] Verify 100% changes via PR (compliance audit)
- [ ] Validate agent accuracy (manual review of decisions)

### Documentation & Demo
- [ ] Write `docs/architecture.md`
- [ ] Create runbooks in `docs/runbooks/` (operational procedures)
- [ ] Create ADRs in `docs/adr/` (key decisions documented)
- [ ] Record final demo video
- [ ] Run `terraform destroy` after demo to stop billing

---

## Ideas / Later
- [ ] Add Redis/DynamoDB for agent state persistence
- [ ] Add Slack/PagerDuty integration for escalation
- [ ] Add AWS X-Ray for distributed tracing
