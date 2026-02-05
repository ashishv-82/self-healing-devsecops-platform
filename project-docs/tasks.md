# Project Tasks: Self-Healing DevSecOps Platform

## Phase 1: Foundation (Infrastructure & Baseline)

### Repository & Local Environment
- [x] Initialize git repository with `.gitignore` and `README.md`
- [x] Create folder structure (`terraform/`, `agent/`, `.github/`, `astronomy-shop/`, `chaos/`, `docs/`, `dashboards/`)
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
  - [x] `docs/runbooks/`
  - [x] `docs/adr/`
- [x] Create `docker-compose.local.yml` with Prometheus, Grafana, and Astronomy Shop
- [x] Create `agent/Dockerfile`
- [x] Create `agent/requirements.txt`
- [x] Create `dashboards/prometheus/prometheus.yml` (minimal config)
- [x] Create `agent/src/main.py` (skeleton app)
- [x] Create `.env.template` for environment variables
- [x] Run `docker-compose up -d --build` to pull images and build Agent
- [x] Verify all 5 containers are running (`docker ps`)
- [x] Verify Agent health check (Fix `src.main` import error)
- [x] (Optional) Add LocalStack service for AWS API mocking

### Terraform Infrastructure
#### 1. Module Implementation (Coding)
- [x] **State Management**: Create `backend.tf` and S3/DynamoDB setup script
- [x] **Networking Module**: Write `modules/networking/main.tf` (VPC, Subnets, IGW)
- [x] **VPC Endpoints**: Add endpoints for ECR, S3, CloudWatch to networking module
- [x] **IAM Module**: Write `modules/iam/main.tf` (Task Execution & Agent Roles)
- [x] **ECS Cluster Module**: Write `modules/ecs-cluster/main.tf` (Fargate Cluster)
- [x] **ALB Module**: Write `modules/alb/main.tf` (Load Balancer, Target Groups)
- [x] **Observability Module**: Write `modules/observability/main.tf` (Log Groups)


#### 2. Environment Configuration
- [x] Create `terraform/environments/dev/main.tf` calling all modules
- [x] Create `terraform/environments/dev/terraform.tfvars` with specific CIDRs/Names
- [x] **Cost Controls**: Add `aws_budgets_budget` resource to root module

#### 3. Execution & Verification
- [x] Run `terraform init` and `terraform validate`
- [x] Run `terraform plan` to confirm resource creation list
- [ ] (Optional) Run `terraform apply` to provision actual AWS resources
- [ ] Verify VPC and ECS Cluster exist via AWS CLI/Console

### CI/CD Setup (GitHub Actions)
- [x] Configure AWS OIDC provider for keyless authentication (Done via Terraform instructions)
- [x] Create `terraform-apply.yml` (Plan on PR, Apply on merge to main)
- [x] Create `docker-build.yml` (Build agent image, push to ECR)
- [x] Create `ecs-deploy.yml` (Trigger ECS service update on new image)
- [x] Create `scheduled-infra.yml` (Scale to 0 at night, scale up in morning)
- [x] Create `dashboard-sync.yml` (Push Grafana JSON to AWS)

### Observability & Baseline Deployment
- [x] Containerize simplified Astronomy Shop services (Using upstream images)
- [x] Containerize simplified Astronomy Shop services (Using upstream images)
- [x] Create Terraform definition for ECS Tasks/Services (`modules/astronomy-shop`)
- [ ] Deploy stack to AWS (via CI/CD or CLI)
- [x] Create `QUICKSTART.md` guidehop to ECS via Terraform
- [ ] **Prometheus**: Deploy self-hosted Prometheus on ECS
- [ ] **Grafana**: Deploy Grafana on ECS with provisioning volume
- [ ] **CloudWatch**: Verify ECS log driver configuration and log group creation

---

## Phase 2: Detection (Observability & Chaos)

### Observability Configuration
- [x] Create `dashboards/prometheus/prometheus.yml` (scrape config for ECS)
- [x] Create `dashboards/prometheus/alerting-rules.yml`
- [x] Create Alertmanager configuration (webhook to agent)
- [x] Create `dashboards/grafana/infra-overview.json`
- [x] Create `dashboards/grafana/agent-activity.json`
- [x] Test alerts locally (trigger fake metric spike)

### Webhook & Signaling
- [x] Create FastAPI `agent/src/main.py` webhook receiver skeleton
- [x] Add rate limiting middleware to webhook endpoint (Skipped for Phase 2, moved to P3)
- [x] Configure Alertmanager to POST to FastAPI on alert
- [x] Validate end-to-end: Metric spike → Alertmanager → Webhook → 200 OK

### Chaos Engineering (Foundation)
- [ ] Install Chaos Toolkit locally
- [x] Create `chaos/experiments/container-crash.yaml`
- [x] Create `chaos/experiments/network-latency.yaml`
- [x] Create `chaos/experiments/cpu-stress.yaml`
- [x] Create `chaos/validation/recovery-checks.py`
- [x] **AWS FIS**: Define FIS experiment templates in Terraform
- [ ] Create `fis-experiment.yml` workflow to trigger FIS from GitHub Actions

---

## Phase 3: AI Agent (The "Brain")

### Core Logic (LangGraph)
- [x] Set up LangGraph project structure in `agent/src/graph/`
- [x] Create `agent/src/graph/state.py` (State schema: AlertInfo, Analysis, Plan)
- [x] Create `agent/src/graph/nodes.py`:
  - [x] Implement `analyst_node` (Query CloudWatch, identify error patterns)
  - [x] Implement `auditor_node` (Query GitHub for recent commits)
  - [x] Implement `decision_node` (Route: InfraFix vs CodeFix vs Escalate)
  - [x] Implement `remediation_node` (Execute fix action)
  - [x] Implement `verification_node` (Check Prometheus after fix)
- [x] Create `agent/src/graph/edges.py` (State transitions, conditional routing)
- [x] Implement LLM confidence thresholds (reject low-confidence decisions)
- [x] Implement circuit breaker (max retries, cooldown period)

### Tool Implementation
- [x] Create `agent/src/tools/cloudwatch_client.py` (filter_log_events)
- [x] Create `agent/src/tools/github_client.py` (get_commits, create_pull_request)
- [x] Create `agent/src/tools/ecs_client.py` (restart_service, update_desired_count)
- [x] Wire tools into LangGraph nodes via tool bindings

### MCP Server (Optional Enhancement)
- [ ] Create `agent/src/mcp/server.py` (MCP protocol handler)
- [ ] Expose agent tools via MCP for external AI integration

### Integration & Deployment
- [x] Write unit tests in `agent/tests/`
- [x] Containerize Agent (finalize Dockerfile)
- [ ] Push Agent image to ECR
- [x] Create ECS Task Definition for Agent
- [x] Grant Agent IAM permissions (ECS, CloudWatch Logs, Bedrock/OpenAI)
- [ ] Deploy Agent to ECS
- [ ] Verify Agent receives webhook and queries CloudWatch in production

---

## Phase 4: Closed-Loop (Remediation & Verification)

### Remediation Workflows
- [x] Implement "Restart" remediation (ECS UpdateService force new deployment)
- [x] Implement "Scale-Up" remediation (increase desired count)
- [x] Implement "Revert Commit" remediation (GitHub PR creation)
- [x] Implement feature flags to enable/disable autonomous actions
- [x] Implement graceful degradation (escalate to human if AI fails)
- [x] Create `agent-pr.yml` workflow (auto-merge agent PRs if tests pass)

### Testing & Validation
- [x] Run full self-healing loop: Chaos → Alert → Agent → Fix → Recovery
- [ ] Measure and record MTTR (Mean Time To Recovery)
- [ ] Verify 100% changes via PR (compliance audit)
- [x] Validate agent accuracy (manual review of decisions)

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
