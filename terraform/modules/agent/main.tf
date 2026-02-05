variable "project_name" {}
variable "environment" {}
variable "vpc_id" {}
variable "private_subnets" { type = list(string) }
variable "cluster_id" {}
variable "alb_security_group_id" {}
variable "app_security_group_id" {}
variable "agent_image" {
  description = "ECR Image URI for the agent"
}
variable "github_token" {}
variable "llm_api_key" {}

# IAM Role for Agent (Task Role - What the container can do)
resource "aws_iam_role" "agent_task_role" {
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

# Permissions for Tools (ECS, CloudWatch, Bedrock)
resource "aws_iam_role_policy" "agent_policy" {
  name = "${var.project_name}-agent-policy-${var.environment}"
  role = aws_iam_role.agent_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:ListTasks"
        ]
        Resource = "*" # Scope down in production
      },
      {
        Effect = "Allow"
        Action = [
          "logs:FilterLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "*"
      }
    ]
  })
}

# CloudWatch Log Group for Agent
resource "aws_cloudwatch_log_group" "agent_logs" {
  name              = "/ecs/${var.project_name}-agent-${var.environment}"
  retention_in_days = 30
}

# ECS Task Definition
resource "aws_ecs_task_definition" "agent" {
  family                   = "${var.project_name}-agent-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.agent_task_role.arn # Ideally separate execution role
  task_role_arn            = aws_iam_role.agent_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "agent"
      image     = var.agent_image
      cpu       = 512
      memory    = 1024
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      environment = [
        { name = "GITHUB_TOKEN", value = var.github_token },
        { name = "LLM_API_KEY", value = var.llm_api_key },
        { name = "AWS_REGION", value = "ap-southeast-2" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.agent_logs.name
          "awslogs-region"        = "ap-southeast-2"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# ECS Service
resource "aws_ecs_service" "agent" {
  name            = "${var.project_name}-agent-${var.environment}"
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.agent.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [var.app_security_group_id]
    subnets          = var.private_subnets
    assign_public_ip = false
  }
}
