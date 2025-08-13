# AWS DevOps AI Agents — Hackathon Edition (V2)
## One-liner
Predictive Auto-Scaling + Self-Healing AI Agent for AWS (ECS Fargate demo) — built for fast hackathon demos with clear metrics, Slack notifications, and repeatable infra provisioning.

## Why this wins
- Combines ML-driven forecasting + automated remediation (scaling & healing).
- Easy to demo: simulate traffic, show scale/heal events, Slack feed, CloudWatch dashboard.
- Judges love cost-saving + reliability + explainability — all included.

## What's inside
- `lambda_agent.py` — improved predictive & self-heal Lambda (single-file, no external deps).
- `terraform/` — skeleton to provision ECS Fargate service + ALB + Lambda + EventBridge + IAM roles.
- `traffic/ab_generate.sh` — quick ApacheBench script to create load during demo.
- `deploy.sh` — helper script that shows recommended deploy steps (not fully automated for safety).
- `README_demo.md` — step-by-step demo script for a 10-min presentation.
- `architecture.mmd` — mermaid diagram (open in mermaid.live) + `architecture.png` placeholder.
- `LICENSE` — MIT

## Quick demo flow (10 minutes)
1. `terraform` apply the demo infra (or run prebuilt CloudFormation).
2. Start traffic generator: `sh traffic/ab_generate.sh http://<ALB_DNS>/ -c 50 -n 10000`.
3. Watch CloudWatch metrics + Slack notifications when Lambda scales/heals.
4. Point judges to CloudWatch dashboard and show number of scale events and healed tasks.

## Files explained
See `terraform/README.md` for infra steps and variables to configure.

## Contact
Built for UD — tweak thresholds and model in `lambda_agent.py` for your app characteristics.
