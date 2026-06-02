# Container Resource Limits

Without resource limits, a single runaway container can exhaust all CPU and memory on a host, taking down every other container. Linux cgroups (the kernel feature under Docker) let you constrain exactly how much CPU, memory, and I/O a container may use.

## Memory Limits

```bash
docker run -d --memory 512m --memory-swap 512m myapp
```

| Flag              | What it controls                                            |
|-------------------|-------------------------------------------------------------|
| `--memory`        | Maximum RAM the container may use                           |
| `--memory-swap`   | RAM + swap combined. Set equal to `--memory` to disable swap |
| `--memory-reservation` | Soft limit — Docker may evict if host is under pressure |

When a container exceeds its memory limit, the Linux OOM killer terminates the most expensive process inside it. If you see exit code **137**, that's an OOM kill.

```bash
docker inspect myapp | grep -i oom
# "OOMKilled": true
```

## CPU Limits

```bash
docker run -d --cpus 1.5 myapp     # up to 1.5 CPU cores
docker run -d --cpu-shares 512 myapp  # relative weight (default 1024)
```

`--cpus` is the simplest option: `--cpus 0.5` means the container gets at most 50% of one core. On a 4-core host, `--cpus 2.0` caps it at 2 full cores.

`--cpu-shares` is a relative weight used when the host is under contention — higher-priority services get more CPU time. It has no effect when the host is idle.

## Process Limits

Prevent fork bombs with `--pids-limit`:

```bash
docker run --pids-limit 200 myapp
```

A fork bomb spawns processes exponentially until the system freezes. A PID limit kills the newest processes once the cap is hit, containing the blast.

## I/O Limits

```bash
docker run -d \
  --device-read-bps /dev/sda:50mb \
  --device-write-bps /dev/sda:50mb \
  myapp
```

Useful on shared hosts where a write-heavy container (log aggregator, database backup) would otherwise saturate disk I/O for all other containers.

## Setting Limits in Compose

```yaml
services:
  api:
    build: .
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 128M
```

The `deploy.resources` key is processed by Docker Swarm and `docker compose up` (with Compose v2). When running outside Swarm, use `mem_limit` and `cpus` at the service level for compatibility:

```yaml
services:
  api:
    build: .
    mem_limit: 512m
    cpus: 1.0
```

## Monitoring Resource Usage

```bash
docker stats                          # live CPU/MEM/NET/I-O for all containers
docker stats myapp --no-stream        # one-shot snapshot
```

Example output:

```
CONTAINER ID  NAME   CPU %   MEM USAGE / LIMIT   MEM %
a1b2c3d4      myapp  0.23%   128MiB / 512MiB     25.0%
```

## Choosing Limits in Practice

1. Run your app under realistic load without limits and observe peak usage with `docker stats`.
2. Set `--memory` to about 1.5× the observed peak to absorb traffic spikes.
3. Set `--cpus` to the number of cores your app actually saturates.
4. Set `--pids-limit` to something generous but finite (200–500 for most apps).

Reasonable limits also make capacity planning predictable: if each container gets 1 CPU and 512 MB, a 4-core/8 GB host can run exactly 8 containers safely.

## Key Takeaways

- Always set memory and CPU limits on production containers.
- OOM kills (exit code 137) mean your memory limit is too low or there's a leak.
- `docker stats` is the fastest way to see what a container actually uses.
- `--pids-limit` is a cheap safety net against fork bombs and runaway spawners.
