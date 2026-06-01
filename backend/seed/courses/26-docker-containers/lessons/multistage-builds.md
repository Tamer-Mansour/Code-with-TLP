# Multi-Stage Builds

Build tools (compilers, package managers, test runners) shouldn't ship in your production image. **Multi-stage builds** let you use a fat builder image, then copy only the final artifact into a minimal runtime image.

## A Go example

```dockerfile
# 1. builder
FROM golang:1.22 AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/app ./cmd/app

# 2. runtime
FROM gcr.io/distroless/static:nonroot
COPY --from=builder /out/app /app
ENTRYPOINT ["/app"]
```

Final image: ~10 MB. The compiler, source code, modules, and tests are gone.

## A Node example

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps  /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
USER node
CMD ["node", "dist/server.js"]
```

Three stages: install prod deps, build, runtime. The final image has only what's needed to run.

## Why it matters

| Image type      | Size      | Attack surface |
|-----------------|-----------|----------------|
| Single-stage    | 1–2 GB    | Compiler + tooling + source |
| Multi-stage     | 50–200 MB | Just the runtime |

Faster pulls, fewer CVEs, smaller logs, happier ops team.

## Target a stage

```bash
docker build --target build -t myapp:debug .
```

Useful for debugging — get a shell inside the builder stage with all the tools intact.

## BuildKit features

Modern Docker uses **BuildKit** by default. It adds:

- Parallel stage execution.
- Inline cache mounts (`RUN --mount=type=cache`).
- Secret mounts (`--mount=type=secret`).
- Better progress UI.

```dockerfile
# Cache the Go module download across builds
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
```

## A common pattern: with-build-args

```dockerfile
ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-alpine AS builder
...
```

Build with:

```bash
docker build --build-arg NODE_VERSION=18 -t myapp .
```

Lets one Dockerfile produce multiple variants without duplication.

## Tip: smaller final stages

Use **distroless** or **scratch** (empty) for the final stage when possible:

```dockerfile
FROM scratch
COPY --from=builder /out/app /app
CMD ["/app"]
```

`scratch` works for **statically linked binaries** (Go with `CGO_ENABLED=0`, Rust musl builds). For dynamically-linked binaries, use `distroless`.

## Don't build inside container

`docker build` builds; you don't `docker run` something that builds. Build-time vs runtime is a clean line — the multi-stage pattern enforces it.
