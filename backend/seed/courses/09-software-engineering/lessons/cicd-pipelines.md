# CI/CD Pipelines: Build, Test, Deploy

Continuous Integration and Continuous Delivery (CI/CD) automate the path from a committed change to running production software. The goal is to make releasing software a low-risk, repeatable, boring activity — not a tense, manual event.

## Continuous Integration (CI)

**Continuous Integration** means every developer merges their changes to the main branch frequently (at least daily), and each merge triggers an automated build and test run.

Without CI, long-lived branches diverge and integrating them becomes painful ("integration hell"). CI surfaces conflicts and test failures early, when they are cheap to fix — not hours before a release deadline.

A typical CI pipeline triggered on every push and pull request:

```
Code push → Checkout → Install deps → Lint → Type check → Unit tests → Integration tests → Build artefact
```

### Complete GitHub Actions CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint-and-type-check:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -r requirements-dev.txt
      - run: ruff check app/                    # linting
      - run: mypy app/ --strict                 # type checking

  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    needs: lint-and-type-check
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest tests/unit/ --cov=app --cov-report=xml --cov-fail-under=80
      - uses: codecov/codecov-action@v4       # upload coverage report

  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: unit-tests
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test_password
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest tests/integration/ -v
        env:
          DATABASE_URL: postgresql://test:test_password@localhost:5432/test_db

  build-docker:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: false          # don't push on PRs, only on main
          tags: myapp:${{ github.sha }}
```

Every PR runs this pipeline. If any step fails, the PR is blocked from merging — the branch protection rules enforce this.

## Continuous Delivery (CD)

**Continuous Delivery** extends CI: the artefact produced by CI is automatically deployed to a staging environment. Deployment to production requires a one-click human approval.

**Continuous Deployment** goes further — every passing build deploys to production automatically, with no human gate. This requires very high test confidence (80%+ coverage, comprehensive E2E tests) and feature flags to hide incomplete work.

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]     # only triggered on main, after PR merge

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: Build and push image
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker push registry.example.com/myapp:${{ github.sha }}
      - name: Deploy to staging
        run: |
          kubectl set image deployment/myapp \
            myapp=registry.example.com/myapp:${{ github.sha }} \
            --namespace=staging

  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production    # requires manual approval in GitHub UI
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/myapp \
            myapp=registry.example.com/myapp:${{ github.sha }} \
            --namespace=production
```

### Deployment Strategies

| Strategy | Description | Rollback | Risk |
|---|---|---|---|
| Big Bang | Replace all instances at once | Requires another deploy | High |
| Rolling | Replace instances one by one | Requires re-deploy | Medium |
| Blue/Green | Run two identical environments; switch traffic atomically | Instant (switch back) | Low |
| Canary | Route a small % of traffic to new version, then ramp | Instant (route to 0%) | Very low |
| Feature Flags | Ship code but toggle features per-user | Toggle the flag off | Near zero |

**Blue/Green in practice:**
```
Production traffic (100%)
        │
        ▼
 ┌─────────────┐
 │  Blue (v2.2)│  ← current production
 └─────────────┘

Deploy v2.3 to Green (zero traffic), run smoke tests,
then switch load balancer:

Production traffic (100%)
        │
        ▼
 ┌─────────────┐
 │ Green (v2.3)│  ← new production
 └─────────────┘
 ┌─────────────┐
 │  Blue (v2.2)│  ← standby for 1 hour, then decommission
 └─────────────┘
```

## Containers and Docker

**Containers** package an application with all its dependencies into an isolated, portable unit. Docker is the most common container runtime.

```dockerfile
# Dockerfile — multi-stage build for smaller production image
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target /app/packages

FROM python:3.12-slim AS runtime
WORKDIR /app
# Copy only installed packages and app code, not build tools
COPY --from=builder /app/packages /app/packages
COPY app/ app/
ENV PYTHONPATH=/app/packages
USER nobody    # don't run as root
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t myapp:latest .
docker run -p 8000:8000 --env-file .env myapp:latest
```

**Container orchestration** (Kubernetes, Docker Swarm) manages running containers across multiple servers: scheduling workloads, health-checking and restarting failed containers, scaling in and out, rolling updates.

## Monitoring and Observability

Deploying is not the end. You need to know whether the deployed software is working in production — before your users tell you.

**The Three Pillars of Observability:**

**1. Logs** — what happened, in sequence:
```python
import structlog

log = structlog.get_logger()

def process_payment(order_id: str, amount: float) -> None:
    log.info("payment.started", order_id=order_id, amount=amount)
    try:
        result = stripe.charge(amount, ...)
        log.info("payment.succeeded", order_id=order_id, charge_id=result.id)
    except stripe.CardError as e:
        log.warning("payment.card_declined", order_id=order_id, error=str(e))
        raise
```

Use **structured logging** (JSON output) so logs can be queried programmatically in Elasticsearch, CloudWatch, or Datadog.

**2. Metrics** — numeric measurements over time:
- `http_requests_total{method="POST", endpoint="/checkout", status="200"}`
- `payment_processing_seconds_p99`
- `active_users_gauge`

Expose metrics in Prometheus format; visualise with Grafana; alert when thresholds breach.

**3. Traces** — the path of a request through multiple services:
```
Trace ID: abc123
  Span: API Gateway (12 ms)
    Span: OrderService.place_order (8 ms)
      Span: DB INSERT orders (3 ms)
      Span: PaymentService.charge (4 ms)
        Span: Stripe API call (3 ms)
    Span: NotificationService.send_email (1 ms)
```

Tools: OpenTelemetry (vendor-neutral instrumentation), Jaeger, Zipkin, Datadog APM.

### SRE Concepts

The **SRE (Site Reliability Engineering)** discipline (from Google's SRE book) formalises reliability with measurable targets:

- **SLI** (Service Level Indicator): the metric being measured (e.g., the fraction of requests that return 2xx in < 500 ms)
- **SLO** (Service Level Objective): your internal target (e.g., 99.9% of requests succeed)
- **SLA** (Service Level Agreement): the contractual commitment to customers (usually less strict than the SLO to give internal headroom)
- **Error Budget:** the allowed downtime before an SLO is breached (99.9% → 8.7 hours/year). When the error budget is nearly exhausted, teams freeze new feature deployments and focus on reliability.

## Infrastructure as Code (IaC)

Rather than clicking through cloud consoles, define infrastructure in code:

```hcl
# Terraform: provision an AWS RDS PostgreSQL instance
resource "aws_db_instance" "main" {
  identifier        = "myapp-prod"
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  storage_encrypted = true

  db_name  = "myapp"
  username = "admin"
  password = var.db_password   # from secrets manager, never hardcoded

  backup_retention_period = 7
  skip_final_snapshot     = false
}
```

IaC makes infrastructure reproducible, reviewable (PR review before applying), and versionable — the same benefits that version control gives to application code. Treat infrastructure changes with the same code review rigour as application changes.
