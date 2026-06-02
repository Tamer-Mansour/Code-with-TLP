# Bind Mounts vs Named Volumes: When to Use Each

Both bind mounts and named volumes persist data outside a container's writable layer, but they have fundamentally different ownership models. Choosing the right one matters for correctness, performance, and security.

## Side-by-Side Comparison

| Dimension          | Named Volume                         | Bind Mount                           |
|--------------------|--------------------------------------|--------------------------------------|
| Path on host       | Docker-managed (`/var/lib/docker/…`) | Any absolute host path you specify   |
| Portability        | Works anywhere Docker runs           | Requires path to exist on host       |
| Performance (Linux)| Excellent                            | Excellent                            |
| Performance (Mac)  | Excellent (VM-backed)                | Slow without VirtioFS / gRPC FUSE    |
| Permissions        | Docker sets UID/GID                  | Mirrors host file ownership          |
| Best for           | Stateful services in prod/staging    | Source code during development       |

## Named Volumes in Practice

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

`docker compose down` keeps `pgdata`. `docker compose down -v` removes it. You can explicitly back it up, snapshot it, or migrate it between hosts.

## Bind Mounts in Practice

```yaml
services:
  api:
    build: .
    volumes:
      - ./src:/app/src    # host ./src → container /app/src
```

You edit `./src/server.js` on the host, and the running container sees the change immediately — no rebuild. This is the canonical development loop for Node, Python, Go, and most interpreted languages.

### The node_modules Trick

A common pitfall: your host may have no `node_modules`, or the wrong platform-specific binaries:

```yaml
services:
  api:
    build: .
    volumes:
      - ./src:/app/src
      - /app/node_modules    # anonymous volume — prevents host from overwriting
```

By declaring `/app/node_modules` as an anonymous volume (no host path), Docker keeps the container-installed modules intact even though `./src` is bind-mounted.

## Performance on macOS and Windows

Docker Desktop on macOS/Windows runs containers inside a Linux VM. Bind mounts cross the VM boundary and were historically slow. Recent versions use **VirtioFS** (macOS) or **WSL2 filesystem** (Windows) to improve throughput, but for large directories (thousands of files) a named volume is still faster.

Rule of thumb:

- If you're watching for file changes (nodemon, air, watchman), accept the bind-mount penalty — convenience wins.
- For node_modules, pip caches, or other large dependency trees, use a named volume to keep performance acceptable.

## Permissions Gotcha

Bind mounts inherit host file ownership:

```bash
# Host file owned by UID 1000
-rw-r--r-- 1 dev dev 1234 config.json

# Inside container (running as UID 10001)
# → permission denied if container user ≠ host UID
```

Solutions: match the UID in your Dockerfile (`USER 1000`), use `chmod` in an entrypoint script, or switch to a named volume where Docker controls the permissions.

## Summary Guidance

Use **named volumes** when:
- Deploying to production or staging.
- Storing database data, uploaded files, or generated artifacts.
- Running on macOS/Windows and performance matters.

Use **bind mounts** when:
- Developing locally and you want hot-reload.
- You need direct access to files from both host tools (editor, linter) and the container.
- The path is well-known and stable (e.g., SSH keys, `/etc/localtime`).
