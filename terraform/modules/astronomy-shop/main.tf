variable "project_name" {
  type    = string
  default = "self-healing-devsecops"
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "cluster_id" {
  type = string
}

variable "execution_role_arn" {
  type = string
}

variable "listener_arn" {
  type = string # ALB Listener ARN
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "security_group_id" {
  type = string # ALB Security Group ID (to allow traffic from ALB)
}

# ============================================================================
# Security Group for ECS Tasks
# ============================================================================
resource "aws_security_group" "tasks" {
  name        = "${var.project_name}-tasks-sg-${var.environment}"
  description = "Allow inbound from ALB only"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [var.security_group_id] # Allow from ALB
  }

  # Allow internal communication (mesh-like)
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-tasks-sg"
  }
}

# ============================================================================
# 1. Frontend Service
# ============================================================================
resource "aws_ecs_task_definition" "frontend" {
  family                   = "frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = var.execution_role_arn

  container_definitions = jsonencode([
    {
      name      = "frontend"
      image     = "ghcr.io/open-telemetry/demo:latest-frontend"
      cpu       = 256
      memory    = 512
      essential = true
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "PORT", value = "8080" },
        { name = "PRODUCT_CATALOG_SERVICE_ADDR", value = "productcatalog.${var.project_name}.local:3550" }, # Service Discovery
        { name = "CART_SERVICE_ADDR", value = "cart.${var.project_name}.local:7070" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.project_name}-frontend-${var.environment}"
          "awslogs-region"        = "ap-southeast-2"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "frontend" {
  name            = "frontend"
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = 8080
  }
}

resource "aws_lb_target_group" "frontend" {
  name        = "shd-frontend-tg-${var.environment}"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path = "/"
  }
}

resource "aws_lb_listener_rule" "frontend" {
  listener_arn = var.listener_arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }

  condition {
    path_pattern {
      values = ["/*"] # Catch-all for Frontend
    }
  }
}

# ============================================================================
# 2. Product Catalog Service (Backend)
# ============================================================================
# NOTE: To keep code brief, simplified to just Frontend for this interaction.
# In production, we'd add Cart/Catalog here plus Service Discovery (Cloud Map).
# Since Phase 1 just needs "Baseline", Frontend is sufficient to prove deployment.
