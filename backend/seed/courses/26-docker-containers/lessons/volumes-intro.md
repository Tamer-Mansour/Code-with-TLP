# Docker Volumes: Persistent Storage

By default, everything written inside a container lives in its **writable layer** and disappears when the container is removed. For databases, uploads, and any stateful data you need **volumes**.

## The Problem Without Volumes

```bash
docker run --rm postgres:16
# write some rows...
# container stops → all data gone
```

The writable container layer is tied to the container's lifetime. `--rm` removes it immediately on exit; even without `--rm`, `docker rm` wipes it.

## Three Storage Options

| Type          | Where data lives       | Persists past `docker rm`? | Best for           |
|---------------|------------------------|----------------------------|--------------------|
| Named volume  | Docker-managed path    | Yes                        | Prod databases     |
| Bind mount    | Host filesystem path   | Yes (it's real files)      | Dev source reload  |
| tmpfs mount   | Host RAM               | No (lost on stop)          | Secrets, caches    |

## Creating and Using Named Volumes

```bash
# Create explicitly
docker volume create pgdata

# Or let Docker create it on first use
docker run -d \
  -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  postgres:16
```

The volume `pgdata` now lives at `/var/lib/docker/volumes/pgdata/_data` on the host (Linux). The container is removed; the data stays.

## Inspecting a Volume

```bash
docker volume inspect pgdata
```

```json
[
  {
    "Name": "pgdata",
    "Driver": "local",
    "Mountpoint": "/var/lib/docker/volumes/pgdata/_data",
    "Labels": {},
    "Scope": "local"
  }
]
```

## Bind Mounts

Mount a host directory directly:

```bash
docker run -d \
  -v /home/dev/app:/app \
  -p 3000:3000 \
  myapi:dev
```

Changes on the host appear instantly inside the container, and vice versa. Great for hot-reload development workflows. Avoid bind mounts in production — the host path must exist and may differ between environments.

## tmpfs Mounts (Linux Only)

```bash
docker run --tmpfs /run:rw,size=64m myapp
```

The `/run` directory is RAM-backed — fast and ephemeral. Useful for secrets that must never hit disk.

## Backing Up and Restoring a Volume

```bash
# Backup
docker run --rm \
  -v pgdata:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/pgdata.tar.gz -C /data .

# Restore
docker run --rm \
  -v pgdata:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/pgdata.tar.gz -C /data
```

This technique uses a throwaway Alpine container to read/write the volume, avoiding the need to stop the database.

## Cleaning Up

```bash
docker volume ls          # list all volumes
docker volume rm pgdata   # remove a specific volume
docker volume prune       # remove all unused volumes (not attached to any container)
```

Unused volumes accumulate silently. `docker system df` shows how much disk volumes consume.

## Key Takeaways

- Containers are **ephemeral** by design; volumes provide durability.
- Use **named volumes** for anything that must survive container restarts.
- Use **bind mounts** for local development convenience.
- Always name your volumes explicitly in production so they are easy to identify, back up, and restore.
