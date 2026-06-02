# Docker Security Best Practices

Containers are not security boundaries by themselves. A misconfigured container running as root, with the Docker socket mounted, is nearly equivalent to root on the host. Security is a deliberate practice.

## 1. Never Run as Root

The single highest-impact change you can make:

```dockerfile
# Create a non-root user
RUN addgroup --system app && adduser --system --ingroup app app
USER app
```

Or with a numeric UID (more portable, no name resolution needed):

```dockerfile
RUN adduser -u 10001 -D app
USER 10001
```

If the process is compromised, it cannot write to `/etc`, install packages, or escape via kernel exploits that require root.

## 2. Use Minimal Base Images

```dockerfile
FROM gcr.io/distroless/java21-debian12   # Java apps — no shell, no package manager
FROM cgr.dev/chainguard/python:latest    # Hardened Python
FROM alpine:3.19                         # Small, auditable
```

Fewer packages = smaller attack surface + faster CVE scanning. Distroless images have no shell, so attackers who get code execution cannot easily explore the container.

## 3. Scan Images for Vulnerabilities

```bash
docker scout cves myapp:latest           # Docker's built-in scanner
trivy image myapp:latest                 # Aqua Trivy (popular OSS)
grype myapp:latest                       # Anchore Grype
```

Integrate scanning into CI so builds fail on critical CVEs.

## 4. Do NOT Mount the Docker Socket

```bash
# NEVER do this in production
docker run -v /var/run/docker.sock:/var/run/docker.sock myapp
```

The Docker socket gives the container full root access to the host — it can start privileged containers, read all other containers' filesystems, and escape completely.

## 5. Drop Capabilities

Linux capabilities grant fine-grained privileges. Drop all, add back only what you need:

```bash
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myapp
```

Common safe set for web services: `NET_BIND_SERVICE` (bind ports < 1024), nothing else.

## 6. Read-Only Root Filesystem

```bash
docker run --read-only --tmpfs /tmp myapp
```

The container cannot write anywhere except `/tmp` (RAM-backed). Malware that tries to drop files onto disk fails immediately.

## 7. Limit Resources

Prevent a compromised or buggy container from taking down the host:

```bash
docker run \
  --memory 512m \
  --cpus 1.0 \
  --pids-limit 200 \
  myapp
```

`--pids-limit` prevents fork bombs.

## 8. Pin Image Digests

Tags are mutable. For production use content-addressable digests:

```bash
docker pull postgres:16@sha256:abc123...
```

Or in Dockerfile:

```dockerfile
FROM postgres:16@sha256:abc123...
```

This guarantees you're running the exact image you tested.

## 9. Secrets Management

Never bake secrets into images:

```bash
# BAD — secret appears in image history
ENV DB_PASSWORD=supersecret

# BETTER — pass at runtime
docker run -e DB_PASSWORD="$DB_PASSWORD" myapp

# BEST — use Docker secrets (Swarm) or Kubernetes secrets
docker secret create db_password ./password.txt
```

## 10. Keep Docker Updated

Docker itself has had container-escape CVEs (`runc` vulnerabilities, `runC` PoCs). Keep Docker Engine and `containerd` up to date.

## Quick Checklist

| Practice                  | Command / Setting                      |
|---------------------------|----------------------------------------|
| Non-root user             | `USER 10001` in Dockerfile             |
| Minimal base image        | `alpine`, `distroless`, `slim`         |
| Read-only filesystem      | `--read-only --tmpfs /tmp`             |
| Drop capabilities         | `--cap-drop ALL --cap-add ...`         |
| No Docker socket mount    | Avoid `-v /var/run/docker.sock:...`    |
| Pin digests               | `FROM image@sha256:...`                |
| Scan for CVEs             | `trivy image` or `docker scout cves`  |
| Resource limits           | `--memory` `--cpus` `--pids-limit`    |

Security is defense in depth — apply as many layers as your threat model requires.
