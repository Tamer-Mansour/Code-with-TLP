# Docker Compose

Compose runs **multi-container apps** from one YAML file. The right tool for "I need a web app + postgres + redis on my laptop."

## A first compose.yaml

```yaml
services:
  web:
    build: .
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgres://postgres:secret@db:5432/app
      REDIS_URL: redis://cache:6379
    depends_on: [db, cache]

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    volumes: ["pgdata:/var/lib/postgresql/data"]
    ports: ["5432:5432"]

  cache:
    image: redis:7

volumes:
  pgdata:
```

Boot the whole stack:

```bash
docker compose up           # foreground
docker compose up -d        # detached
docker compose down         # stop + remove containers (volumes survive)
docker compose down -v      # also remove volumes
docker compose logs -f web
docker compose exec web sh
docker compose ps
```

## Service-to-service DNS

Compose creates a private network. Service names resolve as hostnames — `db` from inside `web` resolves to the postgres container.

## env files

Put secrets and config in `.env`:

```
POSTGRES_PASSWORD=secret
DATABASE_URL=postgres://...
```

```yaml
services:
  web:
    env_file: .env
    environment:
      LOG_LEVEL: info
```

## Override files

Use `compose.override.yaml` (auto-loaded) or `-f` for per-environment configs:

```bash
docker compose -f compose.yaml -f compose.prod.yaml up
```

Common pattern:
- `compose.yaml` — base config.
- `compose.override.yaml` — dev tweaks (volume mounts for live-reload, debugger ports).

## Healthchecks

```yaml
db:
  image: postgres:16
  healthcheck:
    test: ["CMD", "pg_isready", "-U", "postgres"]
    interval: 5s
    timeout: 3s
    retries: 5
```

`depends_on` with `condition: service_healthy` waits for db to be ready before starting web:

```yaml
web:
  depends_on:
    db:
      condition: service_healthy
```

## Build vs image

```yaml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
      target: dev          # multi-stage target
    image: myorg/web:dev   # tag to use after build
```

For pure pre-built images, just `image:`.

## Resource limits

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
```

Compose v2 honors these in `up` mode (not just swarm).

## When NOT to use Compose

For production you'll usually run things on Kubernetes, ECS, Cloud Run, or systemd — not raw Compose. Compose is unbeatable for **local dev** and **CI integration tests**, less ideal for "I'm running this on a server in prod" because of limited orchestration, restart policies, and rolling updates.

## Tips

- One `compose.yaml` per project, in the repo.
- Don't bake secrets into the file — use `.env` (in `.gitignore`) or a secrets manager.
- Use named volumes for stateful services so they survive `docker compose down`.
- `docker compose up --build` rebuilds your image; `--force-recreate` recreates containers.
