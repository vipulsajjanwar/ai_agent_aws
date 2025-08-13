#!/usr/bin/env python3
"""lambda_agent.py
Predictive Auto-Scaling + Self-Heal for ECS Fargate
Dependencies: boto3 (available in Lambda), botocore
Design goals:
- No external heavy deps so it can run in Lambda without layers.
- Simple, robust forecasting (double exponential smoothing)
- Healing heuristics using task statuses and CloudWatch Logs Insights (placeholder)
- Slack notification via webhook stored in SSM or as env var
"""

import os
import json
import math
import time
import logging
from datetime import datetime, timedelta
import urllib.request
import boto3
from botocore.exceptions import ClientError

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

# Configuration - prefer env vars or SSM for secrets/config
CLUSTER = os.getenv('ECS_CLUSTER', 'demo-cluster')
SERVICE = os.getenv('ECS_SERVICE', 'demo-service')
REGION = os.getenv('AWS_REGION', 'us-east-1')
METRIC_NAMESPACE = os.getenv('METRIC_NAMESPACE', 'AWS/ECS')
METRIC_NAME = os.getenv('METRIC_NAME', 'CPUUtilization')
PERIOD = int(os.getenv('METRIC_PERIOD', '60'))  # seconds
LOOKBACK_MINUTES = int(os.getenv('LOOKBACK_MIN', '10'))
PREDICT_AHEAD_MIN = int(os.getenv('PREDICT_AHEAD_MIN', '5'))
TARGET_CPU_PER_TASK = float(os.getenv('TARGET_CPU_PER_TASK', '60.0'))  # percent
SLACK_WEBHOOK_PARAM = os.getenv('SLACK_WEBHOOK_SSM_PARAM')  # optional: name in SSM
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK')  # fallback to direct env

# boto3 clients
boto3.setup_default_session(region_name=REGION)
cw = boto3.client('cloudwatch')
ecs = boto3.client('ecs')
ssm = boto3.client('ssm')

def get_slack_webhook():
    if SLACK_WEBHOOK:
        return SLACK_WEBHOOK
    if SLACK_WEBHOOK_PARAM:
        try:
            resp = ssm.get_parameter(Name=SLACK_WEBHOOK_PARAM, WithDecryption=True)
            return resp['Parameter']['Value']
        except ClientError:
            LOG.exception('Failed to get Slack webhook from SSM param: %s', SLACK_WEBHOOK_PARAM)
    return None

def notify_slack(text):
    webhook = get_slack_webhook()
    if not webhook:
        LOG.info('No Slack webhook configured, skipping notification: %s', text)
        return
    payload = json.dumps({'text': text}).encode('utf-8')
    req = urllib.request.Request(webhook, data=payload, headers={'Content-Type': 'application/json'})
    try:
        res = urllib.request.urlopen(req, timeout=8)
        LOG.info('Slack notified, status=%s', res.status)
    except Exception as e:
        LOG.exception('Failed to send slack notification: %s', e)

def fetch_cw_metric(namespace, name, dimensions, start_time, end_time, period):
    try:
        resp = cw.get_metric_statistics(
            Namespace=namespace,
            MetricName=name,
            Dimensions=dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average']
        )
        dps = resp.get('Datapoints', [])
        # sort ascending by timestamp
        dps_sorted = sorted(dps, key=lambda x: x['Timestamp'])
        return [dp['Average'] for dp in dps_sorted]
    except Exception:
        LOG.exception('Error fetching metric from CloudWatch')
        return []

def double_exponential_smoothing(series, alpha=0.5, beta=0.3, n_preds=1):
    # Holt's linear method (level + trend)
    if not series:
        return 0.0
    if len(series) == 1:
        return series[0]
    # initialize level and trend
    level = series[0]
    trend = series[1] - series[0]
    for i in range(1, len(series)):
        value = series[i]
        last_level = level
        level = alpha * value + (1 - alpha) * (level + trend)
        trend = beta * (level - last_level) + (1 - beta) * trend
    # forecast n_preds steps ahead
    forecast = level + trend * n_preds
    return max(0.0, float(forecast))

def describe_service(cluster, service):
    resp = ecs.describe_services(cluster=cluster, services=[service])
    svc = resp.get('services', [])[0]
    return svc

def list_and_describe_tasks(cluster, service):
    arns = ecs.list_tasks(cluster=cluster, serviceName=service, desiredStatus='RUNNING').get('taskArns', [])
    if not arns:
        return []
    resp = ecs.describe_tasks(cluster=cluster, tasks=arns)
    return resp.get('tasks', [])

def heal_if_needed(cluster, service):
    # Basic heuristic: if runningCount < desiredCount or recent stopped tasks > threshold -> force new deployment
    svc = describe_service(cluster, service)
    desired = svc.get('desiredCount', 1)
    running = svc.get('runningCount', 0)
    LOG.info('Service desired=%s running=%s', desired, running)
    # list stopped tasks for last few minutes (via describe_tasks for recent tasks)
    tasks_all = ecs.list_tasks(cluster=cluster, serviceName=service).get('taskArns', [])
    stopped = 0
    if tasks_all:
        desc = ecs.describe_tasks(cluster=cluster, tasks=tasks_all)
        for t in desc.get('tasks', []):
            if t.get('lastStatus') == 'STOPPED':
                stopped += 1
    LOG.info('stopped tasks count=%s', stopped)
    # threshold based decision
    if running < desired or stopped >= max(1, math.ceil(0.2 * max(1, len(tasks_all)))):
        try:
            ecs.update_service(cluster=cluster, service=service, forceNewDeployment=True)
            notify_slack(f':wrench: Self-heal: forced new deployment for {service} (running={running} desired={desired} stopped={stopped})')
            LOG.info('Forced new deployment for %s', service)
            return True
        except Exception:
            LOG.exception('Failed to force new deployment')
            return False
    return False

def scale_service(cluster, service, new_desired):
    try:
        ecs.update_service(cluster=cluster, service=service, desiredCount=int(new_desired))
        notify_slack(f':rocket: Scaling action: set desiredCount={new_desired} for {service}')
        LOG.info('Scaled service %s to %s', service, new_desired)
        return True
    except Exception:
        LOG.exception('Failed to update service desired count')
        notify_slack(f':x: Failed to scale {service} to {new_desired}')
        return False

def lambda_handler(event, context=None):
    LOG.info('Lambda invoked, event=%s', event)
    # fetch metrics
    end = datetime.utcnow()
    start = end - timedelta(minutes=LOOKBACK_MINUTES)
    dims = [{'Name': 'ClusterName', 'Value': CLUSTER}, {'Name': 'ServiceName', 'Value': SERVICE}]
    series = fetch_cw_metric(METRIC_NAMESPACE, METRIC_NAME, dims, start, end, PERIOD)
    LOG.info('Fetched series (len=%d): %s', len(series), series)
    if not series:
        notify_slack(f':grey_question: Agent: no metric datapoints for {SERVICE}')
        return {'status': 'no_data'}
    # forecast
    # number of periods ahead roughly PREDICT_AHEAD_MIN * 60 / PERIOD
    n_ahead = max(1, math.ceil(PREDICT_AHEAD_MIN * 60 / PERIOD))
    pred = double_exponential_smoothing(series, n_preds=n_ahead)
    LOG.info('Predicted %s ahead by %s min = %.2f', METRIC_NAME, PREDICT_AHEAD_MIN, pred)
    svc = describe_service(CLUSTER, SERVICE)
    desired = svc.get('desiredCount', 1)
    running = svc.get('runningCount', 0)
    # compute required tasks: if predicted average CPU per task * desired > TARGET_CPU_PER_TASK -> scale
    # For demo we approximate pred ~ avg CPU utilization per task; required_tasks = ceil(pred/(TARGET_CPU_PER_TASK/100) * desired)
    # Simpler: required_tasks = ceil((pred/100.0) * desired / (TARGET_CPU_PER_TASK/100.0)) => ceil(pred * desired / TARGET_CPU_PER_TASK)
    try:
        required = max(1, math.ceil((pred * desired) / TARGET_CPU_PER_TASK))
    except Exception:
        required = desired
    LOG.info('Calculated required tasks=%s (desired=%s running=%s)', required, desired, running)
    if required > desired:
        LOG.info('Scaling up to %s', required)
        scale_service(CLUSTER, SERVICE, required)
    elif required < desired:
        # conservative scale down: only if predicted significantly lower
        if desired - required >= 1 and pred < (0.7 * TARGET_CPU_PER_TASK):
            LOG.info('Scaling down to %s', required)
            scale_service(CLUSTER, SERVICE, required)
        else:
            LOG.info('No downscale (safe guard)')
    else:
        LOG.info('No scaling action required')
    # healing
    healed = heal_if_needed(CLUSTER, SERVICE)
    return {'status': 'ok', 'predicted': pred, 'desired': desired, 'required': required, 'healed': healed}

if __name__ == '__main__':
    # local run for testing
    print('Local test run (simulated)')
    print(lambda_handler({}, None))
