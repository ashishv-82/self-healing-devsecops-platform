# Quickstart Guide: Self-Healing DevSecOps Platform

This guide covers how to set up the environment, run the platform locally, and deploy it to AWS.

## 1. Local Development (Docker Compose)
Best for developing the **AI Agent** or **Observability** dashboard without incurring AWS costs.

### Prerequisites
- Docker Desktop installed and running.
- `make` (optional, for shortcuts).

### Steps
1.  **Configure Environment**:
    ```bash
    cp .env.template .env
    # Edit .env and add your LLM_API_KEY (OpenAI/Anthropic)
    ```
2.  **Start the Stack**:
    ```bash
    docker-compose -f docker-compose.local.yml up -d --build
    ```
3.  **Access Services**:
    - **App (Frontend)**: [http://localhost:8080](http://localhost:8080)
    - **Grafana**: [http://localhost:3000](http://localhost:3000) (User: `admin`, Pass: `admin`)
    - **Prometheus**: [http://localhost:9090](http://localhost:9090)
    - **AI Agent Health**: [http://localhost:8000/health](http://localhost:8000/health)
    - **LocalStack**: [http://localhost:4566](http://localhost:4566)

4.  **View Agent Logs**:
    ```bash
    docker logs -f self-healing-devsecops-platform-agent-1
    ```

---

## 2. Infrastructure Deployment (Terraform)
Deploys the production-grade ECS Fargate cluster, VPC, and permissions.

### Prerequisites
- AWS CLI configured (`aws configure`) with Admin permissions.
- Terraform `>= 1.5` installed.

### Initial Setup (One Time Only)
Run the bootstrap script to create the S3 backend bucket and DynamoDB lock table:
```bash
chmod +x terraform/bootstrap_backend.sh
./terraform/bootstrap_backend.sh
```

### Deploying Infrastructure
1.  **Navigate to Dev Environment**:
    ```bash
    cd terraform/environments/dev
    ```
2.  **Configure Variables**:
    ```bash
    cp terraform.tfvars.example terraform.tfvars
    # Edit terraform.tfvars just to confirm values
    ```
3.  **Init & Apply**:
    ```bash
    terraform init
    terraform plan -out=tfplan
    terraform apply tfplan
    ```
    *Note: The first apply takes ~10-15 minutes (NAT Gateways, Clusters).*

---

## 3. CI/CD Pipeline (GitHub Actions)
The repository uses GitHub Actions for automated deployment.

### Required Secrets
Go to **Settings > Secrets and variables > Actions** and add:
- `AWS_ROLE_ARN`: The ARN of the IAM Role GitHub Actions assumes (Output from `oidc-setup` module if added, or create manually).
- `GRAFANA_URL`: (Optional) URL of the Managed Grafana instance.
- `GRAFANA_SERVICE_ACCOUNT_TOKEN`: (Optional) Token for dashboard syncing.

### Workflows
- **Terraform Infrastructure**: Runs on PRs to `main` (Plan) and Pushes (Apply).
- **Build & Push Agent**: Runs when `agent/` changes. Builds Docker image and pushes to ECR.
- **Deploy to ECS**: Runs after Agent build. Updates ECS Service.
- **Scheduled Cost Optimization**: Scales services to 0 at 9 PM and up at 8 AM.

## 4. Run Chaos Experiments (Phase 2)
*(Coming Soon)*
```bash
chaos run chaos/experiments/cpu-stress.yml
```
