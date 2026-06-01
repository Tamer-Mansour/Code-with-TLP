# Lambda and Serverless

Lambda runs your code on demand, in response to events, **without managing servers**. You pay per invocation + execution time. The right call for event-driven workloads, glue code, and APIs with spiky traffic.

## A first Lambda

```python
# handler.py
def handler(event, context):
    name = event.get("name", "world")
    return { "statusCode": 200, "body": f"hello, {name}" }
```

Deploy (manual is rare — use IaC or Serverless Framework):

```bash
zip handler.zip handler.py
aws lambda create-function \
  --function-name hello \
  --runtime python3.12 \
  --handler handler.handler \
  --zip-file fileb://handler.zip \
  --role arn:aws:iam::xxx:role/lambda-basic
```

## Triggers

A Lambda can be triggered by:

- **API Gateway** / **Function URL** — HTTP request.
- **S3** — object created/deleted.
- **DynamoDB Streams**, **Kinesis** — data change events.
- **EventBridge** — cron-like schedules, custom events.
- **SQS** — message queue.
- **Cognito** — user signup / login.
- **Direct invoke** — from your own code.

The event shape differs per source. Always check the docs for the exact JSON.

## Cold starts

First invocation after idle: 100ms–2s while AWS spins up a container with your code. Mitigations:

- **Provisioned Concurrency** — pre-warmed containers, no cold starts (but you pay for them idle).
- **Smaller deploy artifacts** — fewer libraries, less code.
- **Faster runtimes** — Go and Rust cold-start in ~50ms; Python and Node in ~200ms; Java JVM in ~1s+.
- **Lambda SnapStart** for Java — pre-initialized snapshots.

## Limits

- 15-minute max execution.
- 10 GB memory cap (CPU scales with memory).
- 512 MB to 10 GB /tmp.
- Deployment package: 50 MB zipped, 250 MB unzipped. For more, use container images (10 GB).

## Common patterns

### HTTP API

```
Client → API Gateway → Lambda → DynamoDB
```

Lambda + API Gateway + DynamoDB is the "serverless API" stack. Cheap at low scale, no servers to maintain.

### Event-driven

```
S3 object uploaded → Lambda → resize image → S3 (different bucket)
```

### Scheduled jobs

```
EventBridge cron → Lambda → cleanup task
```

Same as cron, no server.

### Stream processing

```
DynamoDB stream / Kinesis → Lambda → notify another system
```

Lambda receives batches automatically.

## Lambda vs Fargate vs ECS

| Need                            | Choose            |
|---------------------------------|-------------------|
| Function-as-a-service, < 15 min | Lambda            |
| Containers, hands-off ops       | Fargate           |
| Containers, more control        | ECS on EC2 or EKS |
| Long-running daemon             | Fargate or EC2    |
| GPU work                        | EC2 / Batch       |

Lambda is the cheapest if your traffic is spiky and total CPU-hours are low. At high constant load, container or EC2 is cheaper per request.

## Don't put DB credentials in env vars

Use **AWS Secrets Manager** or **Parameter Store**:

```python
import boto3
client = boto3.client("secretsmanager")
secret = client.get_secret_value(SecretId="db-creds")
```

Cache the value in a module-level variable so repeated invocations don't re-fetch.

## Frameworks

Writing Lambdas + permissions + API Gateway by hand is tedious. Use:

- **AWS SAM** — official.
- **Serverless Framework** — popular, multi-cloud.
- **AWS CDK** — code-driven IaC.
- **SST** — modern, TypeScript-native.

For real apps, never raw `aws lambda create-function`.
