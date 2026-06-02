# Docker in CI/CD Pipelines

Containers and CI/CD are a natural match: containers give you reproducible build environments, and CI/CD automates building, testing, and pushing images on every code change.

## The Typical Docker CI Workflow

```
code push → CI triggered → build image → run tests inside container
         → scan for CVEs → push to registry → deploy
```

## GitHub Actions Example

```yaml
# .github/workflows/docker.yml
name: Docker Build and Push

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write       # needed to push to ghcr.io

    steps:
      - uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

Key points:
- `cache-from/cache-to: type=gha` uses GitHub Actions layer cache — speeds up repeated builds dramatically.
- The image is only pushed on `main`; PRs only build (fast feedback without publishing).
- The image is tagged with both `latest` and the git SHA.

## Running Tests Inside a Container

Use the image itself as the test runner:

```yaml
      - name: Run tests
        run: |
          docker run --rm \
            -e DATABASE_URL=sqlite:///tmp/test.db \
            ghcr.io/${{ github.repository }}:${{ github.sha }} \
            python -m pytest --tb=short
```

This ensures tests run in exactly the same environment that ships to production.

## CVE Scanning in CI

```yaml
      - name: Scan with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          format: table
          exit-code: 1            # fail the build on critical CVEs
          severity: CRITICAL,HIGH
```

## GitLab CI Example

```yaml
# .gitlab-ci.yml
variables:
  IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind           # Docker-in-Docker
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $IMAGE .
    - docker push $IMAGE
```

GitLab provides `$CI_REGISTRY`, `$CI_REGISTRY_USER`, and `$CI_REGISTRY_PASSWORD` automatically.

## Layer Caching Strategies

| Strategy                | Speed | Complexity | Notes                            |
|-------------------------|-------|------------|----------------------------------|
| `--cache-from` registry | Fast  | Low        | Pull cached layers from registry |
| BuildKit inline cache   | Fast  | Medium     | Embeds cache metadata in image   |
| GitHub Actions cache    | Fast  | Low        | Works only on GitHub Actions     |
| Kaniko (in-cluster)     | OK    | High       | Builds without Docker daemon     |

## Deployment Step

After the image is pushed, a deployment step updates the running service:

```bash
# Kubernetes
kubectl set image deployment/api api=ghcr.io/myorg/myapp:$GIT_SHA

# Docker Swarm
docker service update --image ghcr.io/myorg/myapp:$GIT_SHA myapp_api

# Docker Compose on a VM
ssh deploy@prod "docker compose pull && docker compose up -d"
```

## Key Takeaways

- Build the image once in CI; promote the same artifact through staging to production.
- Use Git SHA tags — never promote `latest` to production.
- Cache layers to keep builds under 2 minutes.
- Integrate CVE scanning so vulnerabilities block the pipeline, not production.
