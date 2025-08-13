# Demo Script (10 minutes)
1. Deploy infra (Terraform) — instructions in terraform/README.md
2. Note ALB DNS from ECS outputs.
3. In terminal run: `sh traffic/ab_generate.sh http://<ALB_DNS>/ -c 50 -n 50000` to simulate load.
4. Open Slack channel where webhook is configured to see agent notifications.
5. Check CloudWatch metrics: CPUUtilization, RequestCount, DesiredCount for ECS service.
6. Explain actions: Lambda predicted spike -> scaled desiredCount -> healed stuck tasks (if any).
7. Wrap up: show predictions log (CloudWatch logs) and S3 telemetry file with predictions.
