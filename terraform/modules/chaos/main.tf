variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "cluster_arn" {
  type = string
}

variable "service_name" {
  type = string
}

resource "aws_iam_role" "fis_role" {
  name = "${var.project_name}-fis-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "fis.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "fis_policy" {
  name = "${var.project_name}-fis-policy-${var.environment}"
  role = aws_iam_role.fis_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:ListTasks",
          "ecs:DescribeTasks",
          "ecs:StopTask"
        ]
        Resource = "*"
      },
    ]
  })
}

resource "aws_fis_experiment_template" "stop_task" {
  description = "Stop ECS Task for ${var.service_name}"
  role_arn    = aws_iam_role.fis_role.arn

  stop_condition {
    source = "none"
  }

  action {
    name      = "stop-ecs-task"
    action_id = "aws:ecs:stop-task"

    target {
      key   = "Tasks"
      value = "TasksToStop"
    }
  }

  target {
    name           = "TasksToStop"
    resource_type  = "aws:ecs:task"
    selection_mode = "COUNT(1)"

    resource_tag {
      key   = "AmazonECSManaged"
      value = "true"
    }

    # In a real scenario, we would use filters to target specific services
    # e.g., cluster_arn and service_name
    parameters = {
      cluster = var.cluster_arn
      service = var.service_name
    }
  }

  tags = {
    Name = "${var.project_name}-fis-stop-task-${var.environment}"
  }
}
