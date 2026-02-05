variable "project_name" {
  type    = string
  default = "self-healing-devsecops"
}

variable "environment" {
  type = string
}

variable "log_retention_days" {
  type    = number
  default = 7
}

locals {
  services = [
    "agent",
    "frontend",
    "cart",
    "productcatalog",
    "currency",
    "recommendation",
    "checkout",
    "redis",
    "ad"
  ]
}

resource "aws_cloudwatch_log_group" "services" {
  for_each = toset(local.services)

  name              = "/ecs/${var.project_name}-${each.key}-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name    = "${var.project_name}-${each.key}-logs"
    Service = each.key
  }
}

output "log_group_names" {
  value = { for s in local.services : s => aws_cloudwatch_log_group.services[s].name }
}
