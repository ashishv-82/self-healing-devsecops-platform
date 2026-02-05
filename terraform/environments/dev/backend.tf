terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket         = "self-healing-devsecops-tfstate-1768220868" # Will be updated by bootstrap script
    key            = "dev/terraform.tfstate"
    region         = "ap-southeast-2"
    encrypt        = true
    dynamodb_table = "self-healing-devsecops-tf-lock"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "self-healing-devsecops"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
