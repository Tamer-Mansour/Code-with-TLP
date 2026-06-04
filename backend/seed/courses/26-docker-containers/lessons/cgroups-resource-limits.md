# Linux Namespaces and cgroups: The Engine Behind Containers

Containers feel like magic, but they are built from two ordinary Linux kernel features: **namespaces** and **control groups (cgroups)**. Understanding them demystifies how Docker works and why containers are not virtual machines.

## Linux Namespaces: Isolation Without a New Kernel

A namespace wraps a global resource so that processes inside it see their own isolated copy. The kernel currently provides six namespaces Docker uses:

| Namespace | What it isolates                              |
|-----------|-----------------------------------------------|
| `PID`     | Process IDs — container's init is PID 1       |
| `NET`     | Network interfaces, routes, firewall rules    |
| `MNT`     | Mount points and the filesystem view          |
| `UTS`     | Hostname and NIS domain name                  |
| `IPC`     | System V IPC, POSIX message queues            |
| `USER`    | User and group IDs (UID/GID mapping)          |

When you run `docker run ubuntu bash`, Docker creates a new set of namespaces and starts the shell inside them. That process sees PID 1, an isolated network stack, and its own hostname — but the host kernel is the same one running everything else. There is no hypervisor, no guest OS boot.

```bash
# See which namespaces your shell is in
ls -la /proc/self/ns/

# PID namespace: container init appears as PID 1 inside
docker run --rm ubuntu ps aux
#  PID  USER  COMMAND
#    1  root  bash
```

## Control Groups: Limiting What Containers Can Consume

Namespaces provide isolation; cgroups provide **resource governance**. A cgroup is a hierarchical grouping of processes with attached resource limits.

Docker creates a cgroup for each container:

```bash
# Limit a container to 512 MB RAM and 1 CPU
docker run -d \
  --memory 512m \
  --memory-swap 512m \
  --cpus 1.0 \
  --name webserver \
  nginx:alpine
```

Under the hood, Docker writes to files like:

```
/sys/fs/cgroup/memory/docker/<id>/memory.limit_in_bytes   → 536870912
/sys/fs/cgroup/cpu/docker/<id>/cpu.cfs_quota_us           → 100000
```

### CPU Shares vs CPU Quotas

Docker exposes two different CPU controls:

- `--cpu-shares` — a **relative weight** (default 1024). If two containers share a busy CPU and one has 2048 shares vs 1024, it gets twice the CPU time. When the host is idle, both get 100%.
- `--cpus` — a **hard quota**: `--cpus 0.5` means at most 50% of one core at any time, regardless of host load.

### Memory Limits

```bash
docker run --memory 256m --memory-swap 256m nginx
```

Setting both to the same value disables swap for the container. If the process exceeds 256 MB, the kernel OOM-killer terminates it. Docker surfaces this as `Exited (137)`.

## Union File Systems: Copy-on-Write Layers

Images are made of **read-only layers** stacked by a union filesystem (OverlayFS on modern Linux). Each container gets a thin **writable layer** on top.

```
Container writable layer  ← writes go here
─────────────────────────
Image layer 3 (COPY . .)  ← read-only
Image layer 2 (RUN npm ci) ← read-only
Image layer 1 (FROM node:20) ← read-only
```

When a container modifies a file from a lower layer, OverlayFS **copies** the file up to the writable layer first — this is copy-on-write. The original layer is never touched. When the container is removed, the writable layer is discarded. Nothing in the image layers changes.

This is why ten containers running the same image share the image bytes on disk rather than each having their own copy.

## Putting It Together

```bash
docker run -d \
  --name api \
  --memory 256m \
  --cpus 0.5 \
  --network mynet \
  --read-only \
  --tmpfs /tmp \
  myapp:1.0
```

This single command:
- Creates 6 namespaces (isolated PID, NET, MNT, UTS, IPC, USER)
- Sets a cgroup: 256 MB RAM limit, 0.5 CPU quota
- Attaches a writable OverlayFS layer on top of `myapp:1.0`'s read-only layers
- Joins the container to the `mynet` network
- Makes the root filesystem read-only (only `/tmp` in RAM is writable)

No VM boot. No hypervisor. Just kernel primitives assembled by the Docker daemon.

## Further Reading

- **MIT Missing Semester — Virtual Machines and Containers**: Anish Athalye et al. contrast VMs and containers at the kernel level, walking through namespaces and cgroups with hands-on exercises. Free at [https://missing.csail.mit.edu/2019/virtual-machines/](https://missing.csail.mit.edu/2019/virtual-machines/)
- **Docker Official Documentation — Get Started Guide**: [https://docs.docker.com/get-started/](https://docs.docker.com/get-started/) covers the architecture end to end.
