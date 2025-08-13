# terraform/variables.tf
variable "region" { default = "us-east-1" }
variable "project" { default = "ai-devops" }
variable "vpc_id" { description = "VPC ID to deploy into" }
variable "public_subnets" { type = list(string) }
variable "private_subnets" { type = list(string) }
variable "container_image" { description = "ECR image URI for demo app" }
