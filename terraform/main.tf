# Terraform skeleton for ECS Fargate + ALB + Lambda (high-level)
# Fill in your VPC, subnets, and container image values.
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" { default = "us-east-1" }
variable "project" { default = "ai-devops" }
variable "vpc_id" { type = string }
variable "private_subnets" { type = list(string) }
variable "public_subnets" { type = list(string) }
variable "container_image" { type = string }

# Resources to create (placeholders):
# - ECS cluster
# - IAM roles: ecsTaskExecutionRole, lambda role
# - ECS task definition & service (Fargate)
# - ALB + target group + listener
# - Lambda function using local file (zip) for the agent
# - EventBridge rule to run Lambda on schedule
# - SSM parameter for Slack webhook

# NOTE: This is a skeleton. For hackathon speed, use AWS console to provision ECS service and paste outputs here.
output "alb_dns" {
  value = aws_lb.demo.dns_name
  description = "ALB DNS name (use this for traffic generator)"
}
