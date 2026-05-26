# Observability and Logging

You cannot improve what you cannot measure, and you cannot debug what you cannot observe. Observability is the practice of instrumenting software so that you can understand its internal state from its external outputs — without having to redeploy or attach a debugger. For production systems, it is not optional.

## The Three Pillars of Observability

### 1. Logs

Logs are time-stamped records of events that happened in your application. They answer: "what happened, in what order?"

**Unstructured vs Structured Logging**

```python
# Unstructured: hard to query programmatically
import logging
logging.info(f"User {user_id} logged in from IP {ip_address}")
# Output: 2024-03-15 14:23:01 INFO User 42 logged in from IP 192.168.1.5

# Structured (JSON): easy to filter, aggregate, and alert on
import structlog
log = structlog.get_logger()
log.info("user.login", user_id=42, ip=ip_address, method="password")
# Output: {"event": "user.login", "user_id": 42, "ip": "192.168.1.5",
#          "method": "password", "timestamp": "2024-03-15T14:23:01Z", "level": "info"}
```

Structured logs can be queried in Elasticsearch, CloudWatch Insights, or Datadog with:
```
event = "user.login" AND ip = "192.168.1.5"
```

**Log Levels** — use them consistently:

| Level | When to use | Example |
|---|---|---|
| `DEBUG` | Detailed internals, off in production | "Loaded config from /etc/app/config.yaml" |
| `INFO` | Normal business events | "User 42 placed order ORD-99 for $49.95" |
| `WARNING` | Unexpected but recoverable situation | "Payment retry 2/3 after timeout" |
| `ERROR` | Something failed and requires attention | "Failed to send confirmation email: SMTP 550" |
| `CRITICAL` | System is in a broken state | "Cannot connect to database after 10 retries" |

**What to log (and what not to):**

Log:
- Request start and completion (method, path, status, duration, user_id)
- External API calls (service name, operation, outcome, latency)
- State transitions in business workflows (order.placed, payment.succeeded, order.shipped)
- Errors with full stack traces and contextual information

Do NOT log:
- Passwords, tokens, API keys, credit card numbers (PII and secrets)
- Extremely high-frequency events (logging every cache lookup would flood your log aggregator)
- Information that duplicates what your metrics already capture

### 2. Metrics

Metrics are numeric measurements collected at regular intervals. They answer: "how is the system performing right now and over time?"

**The Four Golden Signals** (Google SRE book):

| Signal | Description | Example metric |
|---|---|---|
| **Latency** | Time to serve a request | `http_request_duration_seconds_p99` |
| **Traffic** | Request rate | `http_requests_total` (per second) |
| **Errors** | Rate of failed requests | `http_errors_total / http_requests_total` |
| **Saturation** | How "full" the system is | CPU %, memory %, queue depth |

**Prometheus + Python example:**

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

def track_request(method: str, endpoint: str, status: int, duration: float):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
```

Prometheus scrapes the `/metrics` endpoint every 15 seconds. Grafana visualises the time series. Alertmanager fires alerts when thresholds are breached.

**Naming conventions** (Prometheus recommendations):
- Use snake_case: `http_requests_total`, not `httpRequestsTotal`
- Suffix with unit: `_seconds`, `_bytes`, `_total`
- `_total` suffix for counters (monotonically increasing)
- `_ratio` or `_percent` for percentages

### 3. Traces

Distributed traces follow a request as it flows through multiple services, recording timing and metadata at each step (a "span").

```
Request: GET /checkout/summary
  Trace ID: 7f3a2b91

  Span: API Gateway                    [0ms → 45ms]  45ms total
    Span: CartService.get_cart         [2ms → 12ms]  10ms
      Span: Redis GET cart:user:99     [3ms → 5ms]    2ms
    Span: ProductService.get_prices    [12ms → 30ms] 18ms
      Span: DB SELECT products         [13ms → 28ms] 15ms
    Span: TaxService.calculate         [30ms → 42ms] 12ms
      Span: external tax API call      [31ms → 41ms] 10ms
```

A trace reveals that the 10ms external tax API call is the bottleneck — something you'd never see from logs alone.

**OpenTelemetry** is the industry standard for instrumentation. It provides vendor-neutral SDKs that export to any backend (Jaeger, Zipkin, Datadog, Honeycomb):

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

tracer = trace.get_tracer("cart-service")

def get_cart(user_id: int) -> dict:
    with tracer.start_as_current_span("get_cart") as span:
        span.set_attribute("user.id", user_id)
        cart = redis_client.get(f"cart:user:{user_id}")
        span.set_attribute("cart.item_count", len(cart.get("items", [])))
        return cart
```

## Correlation IDs

In a distributed system, a single user action triggers requests across multiple services. Without a **correlation ID** (also called a request ID or trace ID), you cannot find all the log lines related to one request.

```python
import uuid

def create_request_id() -> str:
    return str(uuid.uuid4())

# FastAPI middleware example
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", create_request_id())
    
    # Bind the ID to all log lines for this request
    with structlog.contextvars.bound_contextvars(request_id=request_id):
        response = await call_next(request)
    
    response.headers["X-Request-ID"] = request_id
    return response
```

Now every log line from every service for this request has the same `request_id`. Finding all logs for a failing request:
```
request_id = "7f3a2b91-..."
```

## Alerting

Good alerting is specific, actionable, and not noisy. Alert on **symptoms** (user-visible problems), not **causes** (internal metrics).

| Bad alert | Good alert | Why |
|---|---|---|
| "CPU > 80%" | "Error rate > 1% for 5 minutes" | Users don't care about CPU; they care about errors |
| "Memory usage at 2 GB" | "P99 latency > 2s for checkout endpoint" | High memory may be fine; slow checkout is a business problem |
| "Disk at 85%" | "Disk will fill in < 4 hours at current rate" | Predictive alert gives time to act |

**Alert fatigue** is when alerts fire so often that on-call engineers start ignoring them. Every alert should:
1. Be actionable — there is a specific thing the responder should do
2. Have a runbook — documented steps for diagnosing and resolving it
3. Be reviewed regularly — remove or tune alerts that consistently fire and require no action

## Practical Observability Checklist

Before shipping a service to production:

- [ ] Structured JSON logging with at least INFO level events for all state transitions
- [ ] No secrets, passwords, or PII logged anywhere
- [ ] Request/response logging middleware (method, path, status, duration, user_id)
- [ ] Prometheus metrics endpoint (`/metrics`) exposing request count and latency by endpoint
- [ ] Error rate alert configured (> 1% errors over 5 minutes → page on-call)
- [ ] Latency alert configured (p99 > 2s over 5 minutes → page on-call)
- [ ] Correlation IDs propagated to all downstream service calls
- [ ] Health check endpoint (`/health`) that returns 200 when healthy
- [ ] Runbook written for each alert
- [ ] Tracing instrumented for at least the critical-path endpoints

Observability is not an afterthought — it is a feature that you build into the system from the start.
