# Terraform skeleton README
This folder contains a skeleton Terraform configuration. For the hackathon, you can either:
- Use this skeleton and fill required resources (VPC, subnets, image), or
- Use the AWS Console to quickly create an ECS Fargate Service + ALB, then configure Lambda env vars manually.

Recommended quick path for demo:
1. Create ECS cluster & Fargate service via Console (1 task, simple HTTP container).
2. Create ALB and attach the service to a target group.
3. Create Lambda and paste `lambda_agent.py` as handler (or upload zip).
4. Create EventBridge schedule rule to invoke Lambda every minute.
5. Create an SSM parameter with your Slack webhook and set SLACK_WEBHOOK_SSM_PARAM env var on Lambda.
6. Start load test and show the agent in action.
