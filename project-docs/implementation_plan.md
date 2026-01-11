# Implementation Plan: Self-Healing DevSecOps Platform

## Overview

This document captures **everything needed** to build a production-grade self-healing platform—not just the happy path, but prerequisites, security, testing, error handling, and operational concerns.

---

## 1. Prerequisites (Before Writing Any Code)

### AWS Account Setup
- [ ] Verify AWS account is active and billing is enabled
- [ ] Enable Cost Explorer and set up billing alerts ($25, $50, $75)
- [ ] Create dedicated IAM user for Terraform (or use SSO)
- [ ] Note down AWS Account ID for OIDC configuration
- [ ] Verify region choice (`ap-southeast-2` for Sydney)

### GitHub Repository Setup
- [ ] Create repository if not exists
- [ ] Enable branch protection on `main` (require PR, require status checks)
- [ ] Configure repository secrets:
  - `AWS_ACCOUNT_ID`
  - `AWS_REGION`
  - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
  - `GITHUB_TOKEN` (for agent to create PRs - use fine-grained PAT)
- [ ] Set up GitHub Actions OIDC trust (will be done via Terraform)

### Local Development Tools
- [ ] Docker Desktop installed and running
- [ ] Terraform CLI installed (`>=1.5`)
- [ ] AWS CLI installed and configured with credentials
- [ ] Python 3.11+ installed
- [ ] `uv` or `pip` for Python package management
- [ ] `jq` installed (for JSON parsing in scripts)
- [ ] Chaos Toolkit CLI installed (`pip install chaostoolkit`)

### API Keys & Accounts
- [ ] OpenAI or Anthropic API key obtained
- [ ] Verify API key has sufficient credits/quota
- [ ] GitHub Personal Access Token with `repo` and `workflow` scopes

---

## 2. Developer Experience

### Repository Files
- [ ] `.gitignore` (Python, Terraform, IDE files, `.env`)
- [ ] `.env.example` (template for required environment variables)
- [ ] `Makefile` with common commands:
  - `make up` - Start local Docker Compose
  - `make down` - Stop local stack
  - `make test` - Run all tests
  - `make lint` - Run linters
  - `make plan` - Terraform plan
  - `make apply` - Terraform apply
- [ ] `README.md` with:
  - Project overview
  - Prerequisites list
  - Quick start guide
  - Architecture diagram
  - Contributing guidelines
- [ ] `.pre-commit-config.yaml` for linting/formatting hooks

### Python Project Setup
- [ ] `pyproject.toml` or `requirements.txt` with pinned versions
- [ ] `requirements-dev.txt` (pytest, black, ruff, mypy)
- [ ] Type hints throughout codebase
- [ ] Docstrings for all public functions

### Terraform Organization
- [ ] Use workspaces or separate state files for dev/prod
- [ ] Variables file with descriptions and validation
- [ ] Outputs file for cross-module references
- [ ] Consistent naming convention for all resources

---

## 3. Security Considerations

### Network Security
- [ ] ECS tasks in private subnets (no public IPs)
- [ ] Security groups with minimal ingress rules:
  - ALB: 443 from internet
  - ECS: Only from ALB security group
  - Agent: Only from Alertmanager
- [ ] VPC flow logs enabled for debugging

### Secrets Management
- [ ] Store LLM API key in SSM Parameter Store (SecureString)
- [ ] Store GitHub token in SSM Parameter Store
- [ ] ECS tasks fetch secrets at runtime (not baked into image)
- [ ] Rotate secrets periodically (document procedure)

### IAM Permissions (Least Privilege)
- [ ] **ECS Task Execution Role**: Only ECR pull, CloudWatch logs
- [ ] **Agent Runtime Role**:
  - `ecs:DescribeServices`, `ecs:UpdateService` (specific cluster ARN)
  - `logs:FilterLogEvents` (specific log group ARNs)
  - `bedrock:InvokeModel` OR external API call (no AWS permission)
  - **NOT**: `ecs:*`, `logs:*`, `*:*`
- [ ] Use resource-level permissions, not wildcards
- [ ] Document IAM policy in `docs/iam-policy.md`

### Input Validation
- [ ] Validate Alertmanager webhook payload schema
- [ ] Reject requests without valid signature (if using webhook secret)
- [ ] Sanitize any user/external input before using in AWS API calls
- [ ] Rate limit webhook endpoint (prevent DoS)

### Agent Guardrails
- [ ] Never execute arbitrary code from LLM responses
- [ ] Whitelist allowed remediation actions
- [ ] Maximum actions per incident (circuit breaker)
- [ ] Require human approval for destructive actions (scale to 0, terminate)

---

## 4. Error Handling & Resilience

### What Can Fail?
| Component | Failure Mode | Handling Strategy |
|-----------|-------------|-------------------|
| CloudWatch API | Rate limit, timeout | Exponential backoff, max 3 retries |
| GitHub API | Rate limit (5000/hr) | Check `X-RateLimit-Remaining` header, queue if low |
| ECS API | Service not found, permission denied | Log error, escalate to human |
| LLM API | Rate limit, timeout, invalid response | Retry with backoff, fallback to simpler model |
| Webhook receiver | Overloaded | Return 429, implement queue if needed |

### Error Handling Implementation
- [ ] Create `agent/src/utils/retry.py` with exponential backoff decorator
- [ ] All external API calls wrapped in try/except
- [ ] Structured logging for all errors (JSON format)
- [ ] Correlation ID passed through entire request lifecycle
- [ ] Failed actions logged to CloudWatch with full context

### Circuit Breaker
- [ ] Track consecutive failures per service
- [ ] After N failures, stop attempting fixes for M minutes
- [ ] Alert human when circuit breaker trips
- [ ] Log all circuit breaker state changes

### Graceful Degradation
- [ ] If CloudWatch unavailable → Skip log analysis, use only metrics
- [ ] If GitHub unavailable → Only perform immediate fixes (restart/scale)
- [ ] If LLM unavailable → Escalate immediately to human
- [ ] If ECS API unavailable → Log and alert, do nothing

---

## 5. Testing Strategy

### Unit Tests
- [ ] Test each LangGraph node in isolation
- [ ] Mock all external API calls
- [ ] Test state transitions (edges.py)
- [ ] Test error handling paths
- [ ] Aim for >80% coverage on `agent/src/`

### Integration Tests
- [ ] Test CloudWatch client against LocalStack
- [ ] Test GitHub client against test repository
- [ ] Test ECS client against LocalStack
- [ ] Test full graph execution with mocked tools

### End-to-End Tests
- [ ] Local: Chaos Toolkit → Prometheus → Alertmanager → Agent → Docker restart
- [ ] AWS: FIS → Prometheus → Alertmanager → Agent → ECS restart
- [ ] Record test execution for demo

### Load/Stress Testing
- [ ] Webhook can handle 10 concurrent alerts
- [ ] Agent doesn't crash under rapid-fire alerts
- [ ] Memory usage stays bounded during long runs

### Test Files
- [ ] `agent/tests/test_nodes.py`
- [ ] `agent/tests/test_tools.py`
- [ ] `agent/tests/test_graph.py`
- [ ] `agent/tests/test_webhook.py`
- [ ] `agent/tests/conftest.py` (fixtures)

---

## 6. Observability of the Agent Itself

### Health & Liveness
- [ ] `/health` endpoint returns 200 if agent is healthy
- [ ] `/ready` endpoint returns 200 if agent can process requests
- [ ] ECS health check configured to hit `/health`

### Metrics (Prometheus)
- [ ] `agent_alerts_received_total` (counter)
- [ ] `agent_remediations_attempted_total` (counter, by type)
- [ ] `agent_remediations_successful_total` (counter, by type)
- [ ] `agent_llm_calls_total` (counter, by model)
- [ ] `agent_llm_latency_seconds` (histogram)
- [ ] `agent_decision_confidence` (histogram)

### Logging
- [ ] JSON structured logs
- [ ] Log level configurable via environment variable
- [ ] Every decision logged with:
  - Alert ID
  - Analysis summary
  - Chosen action
  - Confidence score
  - Execution result
- [ ] Sensitive data redacted (API keys, tokens)

### Alerting on Agent Failures
- [ ] Alert if agent health check fails
- [ ] Alert if agent error rate > 10%
- [ ] Alert if agent decision confidence < 50% repeatedly
- [ ] Alert if circuit breaker trips

---

## 7. Deployment & Operations

### ECS Task Configuration
- [ ] Health check: `/health`, interval 30s, timeout 5s
- [ ] Logging: awslogs driver to CloudWatch
- [ ] Auto-scaling: Not needed for demo (single task)
- [ ] Secrets: Injected via SSM at runtime

### Deployment Strategy
- [ ] Rolling deployment (ECS default)
- [ ] Deployment circuit breaker enabled
- [ ] Rollback: Manual via previous task definition

### Runbooks
- [ ] `docs/runbooks/agent-not-responding.md`
- [ ] `docs/runbooks/agent-making-wrong-decisions.md`
- [ ] `docs/runbooks/cost-spike.md`
- [ ] `docs/runbooks/manual-incident-response.md`

### Disaster Recovery
- [ ] Terraform state backed up in S3 with versioning
- [ ] Can rebuild entire infrastructure from code
- [ ] Agent is stateless (no persistent state to recover)

---

## 8. Compliance & Audit

### Change Tracking
- [ ] All infrastructure changes via Terraform (no ClickOps)
- [ ] All code changes via PR (branch protection enforced)
- [ ] Agent PRs have descriptive title and body
- [ ] PR template for agent-created PRs

### Decision Audit Log
- [ ] Every agent decision logged with timestamp
- [ ] Logs retained for 30 days minimum
- [ ] Logs can be queried for incident review
- [ ] Export capability for compliance audits

### Architecture Decision Records
- [ ] `docs/adr/001-cloudwatch-over-loki.md`
- [ ] `docs/adr/002-ecs-fargate-over-eks.md`
- [ ] `docs/adr/003-langgraph-for-agent.md`
- [ ] Template: Problem, Decision, Consequences

---

## 9. Cost Controls (Automation)

### Automated Shutdown
- [ ] GitHub Actions cron job to scale to 0 at 6 PM AEDT
- [ ] GitHub Actions cron job to scale back up at 9 AM AEDT
- [ ] Skip weekends entirely

### Budget Alerts
- [ ] AWS Budget at $25 (warning)
- [ ] AWS Budget at $50 (critical)
- [ ] AWS Budget at $75 (auto-destroy trigger)

### Resource Tagging
- [ ] All resources tagged with `Project=self-healing-platform`
- [ ] All resources tagged with `Environment=dev|prod`
- [ ] Cost allocation report configured

---

## 10. Demo Preparation

### Demo Script
- [ ] Write step-by-step demo script
- [ ] Practice run-through before recording
- [ ] Prepare talking points for each step

### Recording Setup
- [ ] Screen recording software ready
- [ ] Terminal font size increased
- [ ] Browser zoom for Grafana visibility

### Post-Demo
- [ ] `terraform destroy` immediately after recording
- [ ] Verify AWS bill returns to $0
- [ ] Archive recording to Google Drive/YouTube

---

## Summary Checklist

Before starting implementation, verify:
- [ ] All prerequisites completed
- [ ] AWS account and GitHub repo configured
- [ ] Local tools installed
- [ ] API keys obtained
- [ ] This plan reviewed and approved

After each phase, verify:
- [ ] All tests pass
- [ ] No security vulnerabilities
- [ ] Cost within budget
- [ ] Documentation updated
