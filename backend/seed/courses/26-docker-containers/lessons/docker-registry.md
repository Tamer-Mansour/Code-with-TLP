# Docker Registries: Storing and Distributing Images

A **registry** is a storage and distribution system for Docker images. Understanding registries is essential for sharing images across teams, deploying to production, and managing image lifecycles.

## How Registries Work

An image reference has four parts:

```
registry/namespace/repository:tag
  ↓          ↓          ↓       ↓
docker.io   library   nginx   1.25
```

When you run `docker pull nginx`, Docker expands this to `docker.io/library/nginx:latest`.

## Public Registries

| Registry                     | URL                          | Notes                            |
|------------------------------|------------------------------|----------------------------------|
| Docker Hub                   | `docker.io`                  | Default. Free with rate limits.  |
| GitHub Container Registry    | `ghcr.io`                    | Tied to GitHub packages          |
| Google Artifact Registry     | `<region>-docker.pkg.dev`    | Replaces GCR                     |
| Amazon ECR Public            | `public.ecr.aws`             | Free, no rate limits             |
| Quay.io                      | `quay.io`                    | Red Hat / CoreOS                 |

## Pushing an Image

```bash
# 1. Build and tag
docker build -t myapp:1.0 .

# 2. Tag for the registry
docker tag myapp:1.0 ghcr.io/myorg/myapp:1.0

# 3. Authenticate
echo $GITHUB_TOKEN | docker login ghcr.io -u myuser --password-stdin

# 4. Push
docker push ghcr.io/myorg/myapp:1.0
```

Always use a specific tag (e.g. `1.0`, `1.0.3`) in addition to `latest` so older versions remain pullable.

## Pulling From a Private Registry

```bash
docker login registry.example.com
docker pull registry.example.com/myorg/myapp:2.1
```

Kubernetes reads pull secrets to authenticate to private registries.

## Image Tagging Strategy

A common convention used in production:

```
myapp:1.0.3           # semantic version — immutable
myapp:1.0             # minor version — updates with patches
myapp:1               # major version — updates with minors
myapp:latest          # always points to latest stable
myapp:sha-a1b2c3d     # git SHA — guaranteed unique
```

For production deployments, pin to the full semantic version or the git SHA. Never deploy `latest` to production.

## Running a Local Registry

For testing or air-gapped environments:

```bash
docker run -d -p 5000:5000 --name registry registry:2

docker tag myapp:1.0 localhost:5000/myapp:1.0
docker push localhost:5000/myapp:1.0
docker pull localhost:5000/myapp:1.0
```

## Image Cleanup

Images accumulate quickly. Use lifecycle policies in your registry (e.g., "delete untagged images older than 30 days") and locally:

```bash
docker image ls                          # list images
docker image rm myapp:1.0               # remove specific image
docker image prune                      # remove dangling (untagged) images
docker image prune -a                   # remove ALL unused images
docker system prune -a                  # full cleanup (containers + images + volumes + networks)
```

`docker system df` shows disk usage breakdown.

## Content Trust (Notary)

Docker Content Trust signs images so consumers can verify authenticity:

```bash
export DOCKER_CONTENT_TRUST=1
docker push myorg/myapp:1.0             # signs on push
docker pull myorg/myapp:1.0             # verifies on pull
```

For most teams, digest pinning (`@sha256:...`) achieves tamper-evidence without the operational overhead of Notary.

## Key Takeaways

- Every image lives in a registry; Docker Hub is the default.
- Tag images with semantic versions; avoid deploying `latest`.
- Authenticate with `docker login` before pushing to private registries.
- Clean up old images regularly to reclaim disk space and reduce attack surface.
