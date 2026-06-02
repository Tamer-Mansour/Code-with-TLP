# Docker Compose: Networks and Volumes

Docker Compose automatically creates a **shared network** for every project and lets you declare **named volumes** — together these make multi-container wiring almost effortless.

## Auto-Generated Network

When you run `docker compose up`, Compose creates a network named `<project>_default`. Every service joins it automatically, and services can reach each other by service name.

```yaml
services:
  api:
    build: .
    ports:
      - "8080:3000"
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
```

Here `api` connects to `db` at `db:5432` with no extra configuration.

## Custom Networks

Define named networks for finer control — for example to isolate a backend database from a publicly-facing reverse proxy:

```yaml
services:
  nginx:
    image: nginx:alpine
    networks:
      - frontend
  api:
    build: .
    networks:
      - frontend
      - backend
  db:
    image: postgres:16
    networks:
      - backend

networks:
  frontend:
  backend:
```

`db` is only visible to `api`; `nginx` cannot reach `db` directly.

## Named Volumes

A **named volume** is managed by Docker and persists across container restarts and re-creation:

```yaml
services:
  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

`docker compose down` removes containers but **keeps** volumes. Pass `-v` to also remove volumes:

```bash
docker compose down -v   # destroys data — use with care!
```

## Bind Mounts in Compose

For development, bind-mount source code so edits are reflected without rebuilding:

```yaml
services:
  api:
    build: .
    volumes:
      - ./src:/app/src        # bind mount (host path: container path)
      - nodemodules:/app/node_modules  # named volume, prevents overwriting

volumes:
  nodemodules:
```

The named volume for `node_modules` ensures the host folder (which might not exist or be different) doesn't override the container-installed modules.

## Volume Drivers

The default driver stores data in `/var/lib/docker/volumes/`. Plugins let you use NFS, cloud block storage (AWS EBS, Azure Disk), or distributed filesystems like GlusterFS — just change the driver:

```yaml
volumes:
  pgdata:
    driver: local
    driver_opts:
      type: nfs
      o: addr=nas.example.com,rw
      device: ":/exports/pgdata"
```

## Inspecting Volumes

```bash
docker volume ls
docker volume inspect <volume-name>
docker volume rm <volume-name>
docker volume prune          # remove all unused volumes
```

## Summary Table

| Feature         | Named Volume                   | Bind Mount                    |
|-----------------|-------------------------------|-------------------------------|
| Managed by      | Docker                        | Host filesystem               |
| Data survives   | `docker compose down`         | Always (it's a real folder)   |
| Best for        | Databases, uploads in prod    | Dev source code hot-reload    |
| Declared in     | `volumes:` section            | Inline host path              |

Understanding Compose networking and volumes lets you build realistic local environments that closely mirror production — databases with persisted data, isolated network segments, and live code reloading for development.
