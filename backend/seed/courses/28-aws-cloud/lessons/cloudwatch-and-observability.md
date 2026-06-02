# CloudWatch and Observability on AWS

Observability is knowing what your system is doing from the outside. On AWS, **Amazon CloudWatch** is the central hub for logs, metrics, alarms, and dashboards. This lesson covers the three pillars — logs, metrics, traces — and how CloudWatch covers them.

## Logs

**CloudWatch Logs** collects log streams from virtually every AWS service and your own applications.

```bash
# Tail logs from a Lambda function
aws logs tail /aws/lambda/my-function --follow

# Query logs with CloudWatch Logs Insights
aws logs start-query \
  --log-group-name /aws/lambda/my-function \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 50'
```

### Log groups and retention

By default, CloudWatch Logs retains data indefinitely — and charges for storage. Always set a retention policy:

```bash
aws logs put-retention-policy \
  --log-group-name /aws/lambda/my-function \
  --retention-in-days 30
```

| Retention period | Use case                              |
|------------------|---------------------------------------|
| 7 days           | Dev environments                      |
| 30 days          | Staging                               |
| 90 days          | Production (most workloads)           |
| 365+ days        | Compliance-mandated (use S3 export)   |

## Metrics

CloudWatch collects **metrics** — time-series data points — from AWS services automatically. EC2 sends CPU, network, disk. RDS sends connections, latency, IOPS. Lambda sends duration, errors, throttles.

```bash
# Get EC2 CPU utilization for the past hour
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-xxx \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Average
```

For application-level metrics, publish custom metrics:

```python
import boto3

cw = boto3.client("cloudwatch")
cw.put_metric_data(
    Namespace="MyApp/Payments",
    MetricData=[{
        "MetricName": "PaymentProcessed",
        "Value": 1,
        "Unit": "Count",
        "Dimensions": [{"Name": "Environment", "Value": "prod"}]
    }]
)
```

## Alarms

An **alarm** watches a metric and transitions between OK, ALARM, and INSUFFICIENT_DATA states:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name high-error-rate \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --dimensions Name=FunctionName,Value=my-function \
  --statistic Sum \
  --period 60 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:xxx:alerts-topic \
  --treat-missing-data notBreaching
```

Best practice: alarm on **error rate**, not just error count. Two errors in 1000 requests is fine; two errors in 5 requests is a problem.

## Dashboards

Dashboards let you visualize metrics side by side:

```bash
aws cloudwatch put-dashboard \
  --dashboard-name production \
  --dashboard-body file://dashboard.json
```

A good production dashboard shows: request rate, error rate, P50/P95/P99 latency, CPU/memory, queue depth, and active alerts.

## Distributed Tracing with AWS X-Ray

**X-Ray** instruments your application to trace requests as they flow through services (Lambda → DynamoDB → SQS → another Lambda):

```python
from aws_xray_sdk.core import xray_recorder, patch_all
patch_all()  # patches boto3, requests, etc.

@xray_recorder.capture('process_payment')
def process_payment(order):
    # X-Ray records a subsegment here
    ...
```

X-Ray shows you a **service map** and flame graph so you can find which downstream call is slow.

## Amazon Managed Grafana and OpenSearch

For large-scale observability, AWS offers:

- **Amazon Managed Grafana** — visualize metrics from CloudWatch, X-Ray, and other sources with Grafana dashboards.
- **OpenSearch Service** — Elasticsearch-compatible, great for log search at scale. Export CloudWatch logs to OpenSearch via Kinesis Firehose.

## Observability checklist

- [ ] All services log to CloudWatch with a retention policy set.
- [ ] Alarms on error rate, latency P99, and queue depth.
- [ ] At least one SNS topic routes alarms to email/Slack/PagerDuty.
- [ ] Custom metrics for business-level KPIs (payments processed, sign-ups).
- [ ] X-Ray enabled for Lambda and API Gateway in production.
- [ ] A dashboard that shows the system at a glance.
