# AWS DevOps AI Agents

## Overview
This project showcases **AI-powered AWS DevOps Agents** designed for automating infrastructure tasks, monitoring, scaling, and optimization. 
It is intended for hackathon-level prototyping but follows production-grade best practices.

## Features
- **Infrastructure Provisioning Agent**: Provisions AWS resources (EC2, S3, RDS, ECS) using AI decisions based on workload.
- **Monitoring & Anomaly Detection Agent**: Uses CloudWatch metrics and AI to predict outages or failures.
- **Auto-Scaling Optimization Agent**: Predictive scaling for ECS, EKS, and EC2 instances.
- **Cost Optimization Agent**: AI-driven analysis of AWS billing to suggest savings.
- **Security & Compliance Agent**: Detects vulnerabilities and applies patches automatically.

## Architecture Diagram
![Architecture](architecture.png)

## Components
1. `infrastructure_agent.py` - AI-based provisioning logic.
2. `monitoring_agent.py` - CloudWatch-based anomaly detection.
3. `autoscaling_agent.py` - Predictive scaling logic.
4. `cost_agent.py` - Billing data optimization suggestions.
5. `security_agent.py` - Vulnerability detection and patching.

## How to Run
1. Install dependencies:
    ```bash
    pip install boto3 openai pandas scikit-learn
    ```
2. Configure AWS CLI:
    ```bash
    aws configure
    ```
3. Run an agent:
    ```bash
    python infrastructure_agent.py
    ```

## License
MIT License
