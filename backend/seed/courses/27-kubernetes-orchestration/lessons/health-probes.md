# Health Probes in Kubernetes

Kubernetes needs a way to know whether your container is alive and ready to serve traffic. Three probe types give you fine-grained control over this: **liveness**, **readiness**, and **startup**.

## Why Probes Matter

Without probes, K8s has no visibility into your application's internal state. A container that is running (from the OS's perspective) but wedged in a deadlock will keep receiving traffic and never be restarted. Probes close that gap.

## Liveness Probe

A **liveness probe** restarts the container when it fails. Use it to detect deadlocks or fatal states the container cannot recover from on its own.

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3
```

- `initialDelaySeconds` — wait before the first check (give the app time to boot).
- `periodSeconds` — check frequency.
- `failureThreshold` — how many consecutive failures trigger a restart.

## Readiness Probe

A **readiness probe** controls whether the Pod receives traffic from a Service. A pod that fails readiness is removed from the Service's endpoint list but is **not restarted**.

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  periodSeconds: 5
  failureThreshold: 2
```

Use readiness when your app needs time to warm up (e.g., loading a large ML model into memory) or when it temporarily goes unready due to an upstream dependency being unavailable.

## Startup Probe

A **startup probe** is for slow-starting containers. It disables liveness until startup succeeds, preventing premature restarts.

```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
```

The above gives the container up to 300 seconds (30 × 10) to start before liveness takes over.

## Probe Mechanisms

| Mechanism      | How It Works                                            |
|----------------|---------------------------------------------------------|
| `httpGet`      | HTTP GET; success = 200–399 status code                 |
| `tcpSocket`    | Checks if a TCP port accepts connections                |
| `exec`         | Runs a command inside the container; success = exit 0   |
| `grpc`         | gRPC health protocol (K8s 1.23+)                        |

## Worked Example — Web API

```yaml
containers:
- name: api
  image: myapi:2.1
  ports:
  - containerPort: 8080
  startupProbe:
    httpGet: { path: /healthz, port: 8080 }
    failureThreshold: 20
    periodSeconds: 5
  readinessProbe:
    httpGet: { path: /ready, port: 8080 }
    periodSeconds: 5
    failureThreshold: 2
  livenessProbe:
    httpGet: { path: /healthz, port: 8080 }
    periodSeconds: 15
    failureThreshold: 3
```

## Common Mistakes

- **No `initialDelaySeconds` on liveness** — causes restart loops on slow-starting apps.
- **Liveness and readiness on the same endpoint** — liveness restarting when you only want to shed traffic. Keep them separate.
- **Probe path that requires auth** — K8s cannot authenticate; use a public health endpoint.
- **Setting `failureThreshold: 1` on liveness** — one transient network glitch restarts your container. Use 3+.
