module "networking" {
  source = "../../modules/networking"

  vpc_cidr    = var.vpc_cidr
  environment = var.environment
}

module "iam" {
  source = "../../modules/iam"

  environment = var.environment
}

module "ecs_cluster" {
  source = "../../modules/ecs-cluster"

  environment = var.environment
}

module "alb" {
  source = "../../modules/alb"

  environment    = var.environment
  vpc_id         = module.networking.vpc_id
  public_subnets = module.networking.public_subnet_ids
}

module "observability" {
  source = "../../modules/observability"

  environment = var.environment
}

module "astronomy_shop" {
  source = "../../modules/astronomy-shop"

  environment        = var.environment
  vpc_id             = module.networking.vpc_id
  cluster_id         = module.ecs_cluster.cluster_id
  execution_role_arn = module.iam.execution_role_arn
  listener_arn       = module.alb.listener_arn
  private_subnet_ids = module.networking.private_subnet_ids
  security_group_id  = module.alb.security_group_id # ALB SG (to allow traffic)
}

# ============================================================================
# Cost Controls (Budget)
# ============================================================================
resource "aws_budgets_budget" "cost_control" {
  name              = "self-healing-devsecops-budget-${var.environment}"
  budget_type       = "COST"
  limit_amount      = "50"
  limit_unit        = "USD"
  time_period_start = "2024-01-01_00:00"
  time_unit         = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 50
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = ["ashishv82@example.com"] # Replace with variable later
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = ["ashishv82@example.com"]
  }
}
