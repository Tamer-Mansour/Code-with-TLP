# Healthchecks and Restart Policies

Running a container is not the same as running a healthy service. Docker provides **health checks** to detect when an application is broken and **restart policies** to recover automatically.

## HEALTHCHECK in Dockerfile

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm ci

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
```

Parameters:

| Parameter        | Default | Meaning                                              |
|------------------|---------|------------------------------------------------------|
| `--interval`     | 30s     | How often to run the check                           |
| `--timeout`      | 30s     | Max time a single check may take                     |
| `--start-period` | 0s      | Grace period after startup before checks count       |
| `--retries`      | 3       | Consecutive failures before status becomes unhealthy |

## Health Status

```bash
docker ps              # shows Up (healthy), Up (unhealthy), or Up (starting)
docker inspect myapp   # detailed health check history
```

The three states:
- **starting** — within `start-period`, failures don't count yet
- **healthy** — last check succeeded
- **unhealthy** — `retries` consecutive failures

## Using HEALTHCHECK at Runtime

Override or add a healthcheck without rebuilding:

```bash
docker run -d \
  --health-cmd "curl -f http://localhost/ping || exit 1" \
  --health-interval 20s \
  --health-retries 5 \
  nginx
```

## Restart Policies

Tell Docker what to do when a container exits:

```bash
docker run --restart unless-stopped myapp
```

| Policy               | Behavior                                                   |
|----------------------|------------------------------------------------------------|
| `no`                 | Never restart (default)                                    |
| `on-failure[:N]`     | Restart only on non-zero exit; limit to N retries          |
| `always`             | Always restart, even after `docker stop` or reboot        |
| `unless-stopped`     | Like `always` but respects an explicit `docker stop`       |

For production services: **`unless-stopped`** is usually the right choice. `always` also restarts containers you deliberately stopped, which can be surprising.

## Restart Policies in Compose

```yaml
services:
  api:
    build: .
    restart: unless-stopped
  worker:
    build: .
    restart: on-failure
```

## Combining Health and Restart

Docker Compose can use health status to order service startup:

```yaml
services:
  api:
    build: .
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

`api` only starts after `db` reports **healthy** — no more race conditions where the API crashes because the database isn't ready.

## Practical /health Endpoint

Every API should expose a lightweight health endpoint:

```javascript
// Node/Express
app.get('/health', (req, res) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});
```

```python
# FastAPI
@app.get("/health")
def health():
    return {"status": "ok"}
```

Return HTTP 200 when healthy, 503 when degraded. Keep it fast — no database queries if possible.

## Key Takeaways

- Always define a `HEALTHCHECK` for long-running services so Docker knows when they're broken.
- Use `unless-stopped` as your default restart policy for production containers.
- In Compose, combine `healthcheck` + `depends_on.condition: service_healthy` to eliminate startup race conditions.
