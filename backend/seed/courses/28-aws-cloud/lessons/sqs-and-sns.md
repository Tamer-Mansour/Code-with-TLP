# SQS and SNS - Messaging and Event Distribution

Decoupling services with queues and topics is one of the most effective ways to build reliable, scalable systems. AWS provides **SQS** (Simple Queue Service) for point-to-point queues and **SNS** (Simple Notification Service) for fan-out pub/sub.

## SQS — Simple Queue Service

SQS is a managed message queue. Producers send messages; consumers poll and process them. The queue buffers messages so producers and consumers can scale and fail independently.

### Queue types

| Type      | Behavior                                             |
|-----------|------------------------------------------------------|
| Standard  | At-least-once delivery, best-effort ordering         |
| FIFO      | Exactly-once processing, strict ordering, 3,000 TPS  |

Use **FIFO** when order and deduplication matter (financial transactions, order state machines). Use **Standard** for everything else — it scales to unlimited TPS.

### Send and receive messages

```python
import boto3, json

sqs = boto3.client("sqs")
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/123456789/orders"

# Send
sqs.send_message(
    QueueUrl=QUEUE_URL,
    MessageBody=json.dumps({"order_id": 42, "amount": 99.99})
)

# Receive (long polling)
response = sqs.receive_message(
    QueueUrl=QUEUE_URL,
    MaxNumberOfMessages=10,
    WaitTimeSeconds=20  # long polling — wait up to 20s for messages
)
for msg in response.get("Messages", []):
    body = json.loads(msg["Body"])
    print("Processing order", body["order_id"])
    # delete only after successful processing
    sqs.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=msg["ReceiptHandle"]
    )
```

### Visibility timeout

When a consumer receives a message, it becomes **invisible** for the visibility timeout (default 30s). If the consumer doesn't delete it in time, the message becomes visible again for another consumer to try. This provides automatic retry on failure.

Set the visibility timeout longer than your maximum processing time:

```bash
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/xxx/orders \
  --attributes VisibilityTimeout=300
```

### Dead-letter queues (DLQ)

If a message fails processing N times, SQS moves it to a **dead-letter queue** for investigation:

```bash
aws sqs set-queue-attributes \
  --queue-url $MAIN_QUEUE_URL \
  --attributes '{
    "RedrivePolicy": "{\"deadLetterTargetArn\":\"arn:aws:sqs:us-east-1:xxx:orders-dlq\",\"maxReceiveCount\":3}"
  }'
```

Always set up a DLQ. Alert on DLQ depth to catch processing failures early.

### Lambda + SQS

Lambda can consume SQS natively — no polling code needed:

```bash
aws lambda create-event-source-mapping \
  --function-name process-order \
  --event-source-arn arn:aws:sqs:us-east-1:xxx:orders \
  --batch-size 10 \
  --maximum-batching-window-in-seconds 5
```

Lambda polls SQS, calls your function with a batch of messages, and deletes successful ones. Failed items are retried up to `maxReceiveCount`.

## SNS — Simple Notification Service

SNS is a pub/sub service. Publishers send to a **topic**; SNS fans out to all **subscriptions** (SQS queues, Lambda functions, HTTP endpoints, email, SMS).

### Fan-out pattern

```
Payment Service → SNS topic: payment-processed
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
         SQS queue   SQS queue  Lambda
         (invoice)   (loyalty)  (analytics)
```

Each downstream service processes at its own pace without knowing about the others. Adding a new subscriber doesn't change the publisher.

```python
import boto3

sns = boto3.client("sns")
TOPIC_ARN = "arn:aws:sns:us-east-1:xxx:payment-processed"

sns.publish(
    TopicArn=TOPIC_ARN,
    Message=json.dumps({"order_id": 42, "status": "paid"}),
    Subject="PaymentProcessed"
)
```

### Message filtering

Subscribers can filter messages so they only receive relevant ones:

```bash
# This SQS subscription only receives high-value orders
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:xxx:payment-processed:yyy \
  --attribute-name FilterPolicy \
  --attribute-value '{"amount": [{"numeric": [">=", 1000]}]}'
```

## Patterns to remember

| Pattern                     | Implementation              |
|-----------------------------|-----------------------------|
| Work queue (1 producer, N workers) | SQS Standard + multiple consumers |
| Guaranteed ordering         | SQS FIFO                    |
| Fan-out to many systems     | SNS + multiple SQS queues   |
| Email / SMS alerts          | SNS with email/SMS sub      |
| Decouple async processing   | SQS between services        |
| Event-driven Lambda         | SNS → Lambda or SQS → Lambda |

## Cost

- SQS: first 1M requests/month free; ~$0.40 per million after.
- SNS: first 1M publishes/month free; ~$0.50 per million after. SMS is per-message (higher, varies by country).
- Data transfer within the same region between SQS/SNS and Lambda/EC2 is free.
