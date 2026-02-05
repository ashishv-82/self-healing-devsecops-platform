variable "project_name" {
  type    = string
  default = "self-healing-devsecops"
}

variable "environment" {
  type = string
}

# ============================================================================
# 1. ECS Task Execution Role (Standard AWS Managed)
# Used by ECS Agent to pull images (ECR) and push logs (CloudWatch)
# ============================================================================

resource "aws_iam_role" "ecs_execution" {
  name = "${var.project_name}-ecs-execution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Add SSM access for secrets (if using SSM Parameter Store for secrets)
resource "aws_iam_role_policy" "ecs_execution_ssm" {
  name = "${var.project_name}-ecs-execution-ssm"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "secretsmanager:GetSecretValue"
        ]
        Resource = "*" # Restrict this in production to specific ARN
      }
    ]
  })
}


# ============================================================================
# 2. Agent Runtime Role (Custom Least Privilege)
# Used by the Python Agent Code to "Self-Heal"
# ============================================================================

resource "aws_iam_role" "agent_task" {
  name = "${var.project_name}-agent-task-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "agent_policy" {
  name        = "${var.project_name}-agent-access-policy-${var.environment}"
  description = "Allows Agent to query logs, invoke Bedrock, and restart ECS services"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Observability: Read CloudWatch Logs
      {
        Effect = "Allow"
        Action = [
          "logs:FilterLogEvents",
          "logs:GetLogEvents",
          "logs:DescribeLogGroups"
        ]
        Resource = "*" # Scope to project log groups
      },
      # Remediation: Restart/Update ECS Services
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:ListTasks"
        ]
        Resource = "*" # Scope to project cluster
      },
      # AI: Invoke Bedrock
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "*" # Scope to specific model
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "agent_attach" {
  role       = aws_iam_role.agent_task.name
  policy_arn = aws_iam_policy.agent_policy.arn
}

# Outputs
output "execution_role_arn" {
  value = aws_iam_role.ecs_execution.arn
}

output "agent_task_role_arn" {
  value = aws_iam_role.agent_task.arn
}
