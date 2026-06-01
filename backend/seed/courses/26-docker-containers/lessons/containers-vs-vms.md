# Containers vs VMs

A **container** is a process (or set of processes) isolated from the host using Linux kernel features — namespaces (PID, network, mount, etc.) and cgroups (CPU, memory limits). A **VM** is a full guest OS running on a hypervisor.

```
  Container               VM
  ─────────              ─────────
  app code               app code
  libs                   libs
  ↓ shared kernel        guest OS
  host kernel            hypervisor
                         host kernel
```

## What this means in practice

| Property         | Container          | VM                |
|------------------|--------------------|-------------------|
| Startup time     | Milliseconds       | Seconds–minutes   |
| Memory overhead  | ~MBs               | ~GBs              |
| Density per host | Hundreds–thousands | Dozens            |
| Isolation        | Process-level      | Hardware-level    |
| OS choice        | Same kernel as host| Any guest OS      |

Containers trade some isolation for huge gains in density and speed. For modern web services that's the right trade.

## Why "Docker"

Docker is the most popular toolchain for working with containers, not the only one — `podman`, `containerd`, `nerdctl`, `buildah` are all interoperable via the OCI standard.

Most people informally use "Docker" to mean "container," but the runtime under Kubernetes is usually `containerd`, not Docker.

## A first container

```bash
docker run --rm -it ubuntu:24.04 bash
```

Pulls the image, starts a container, drops you into a shell. `exit` to leave; `--rm` removes the container on exit.

## Images vs containers

- **Image** — a built artifact (filesystem snapshot + metadata).
- **Container** — a running (or stopped) instance of an image.

Many containers can share one image. The image is read-only; each container gets a thin writable layer on top.

## Layers

An image is a stack of read-only layers. Each instruction in a `Dockerfile` adds one. Identical layers are reused across images, saving disk and bandwidth.

That's why a well-ordered Dockerfile caches well and a poorly-ordered one rebuilds everything on every change.

## Registry

Images live in **registries**: Docker Hub, GitHub Container Registry, Amazon ECR, Google Artifact Registry, etc.

```bash
docker pull node:20-alpine
docker push myorg/myapp:1.0.3
```

The tag (`:1.0.3`, `:latest`, `:alpine`) is mutable — different teams have different conventions. Production should pin to a digest:

```bash
docker pull node:20-alpine@sha256:abcd...
```

## When NOT to use containers

- Truly trusted, simple, single-process deployments — sometimes a `systemd` unit is enough.
- Strong multi-tenant isolation (use VMs or microVMs like Firecracker).
- Native GUI applications.

For everything else — backend services, build environments, dev shells — containers are the modern default.
