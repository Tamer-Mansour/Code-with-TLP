# Pods and Deployments

## Pod

A **Pod** is one or more containers that share a network namespace and (optionally) volumes. The Pod is the smallest unit K8s schedules. You rarely create a Pod directly — you let a Deployment do it.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
  labels: { app: web }
spec:
  containers:
  - name: web
    image: nginx:1.27
    ports: [ { containerPort: 80 } ]
    resources:
      requests: { cpu: 100m, memory: 128Mi }
      limits:   { cpu: 500m, memory: 512Mi }
```

- **requests** — what the scheduler reserves on a node.
- **limits** — what the container cannot exceed (CPU is throttled, memory triggers OOMKilled).

Always set both for production workloads.

## Deployment

A Deployment manages a ReplicaSet, which manages Pods. It handles rolling updates and rollbacks.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels: { app: web }
  template:
    metadata:
      labels: { app: web }
    spec:
      containers:
      - name: web
        image: ghcr.io/me/web:1.2.3
        ports: [ { containerPort: 80 } ]
        readinessProbe:
          httpGet: { path: /health, port: 80 }
          periodSeconds: 5
        livenessProbe:
          httpGet: { path: /alive, port: 80 }
          initialDelaySeconds: 15
```

The `selector` must match the labels in the pod `template`. K8s uses labels for everything — services, scaling, monitoring.

## Probes

- **livenessProbe** — restart the container if it fails.
- **readinessProbe** — stop sending traffic until it passes.
- **startupProbe** — slow-starting apps; give them time before liveness kicks in.

Without probes, K8s can't tell if your app is wedged. Always define at least readiness for HTTP services.

## Rolling updates

A Deployment rolls out replacing one pod at a time:

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

`maxSurge: 1` = one extra pod allowed during update. `maxUnavailable: 0` = always keep the target count serving.

## Trigger a new rollout

Change anything in the pod template — image tag, env var, label — and `kubectl apply`. Or:

```bash
kubectl set image deploy/web web=ghcr.io/me/web:1.2.4
kubectl rollout status deploy/web
kubectl rollout undo deploy/web      # quick revert
```

## Pod lifecycle

```
Pending → ContainerCreating → Running → Succeeded / Failed
                                      ↘ CrashLoopBackOff
```

If you see `CrashLoopBackOff`:

```bash
kubectl logs web-abc --previous       # logs from the just-crashed container
kubectl describe pod web-abc          # events at the bottom
```

## Multiple containers in a Pod

Sometimes you want a sidecar — a helper container alongside the main one (e.g., log shipper, proxy):

```yaml
spec:
  containers:
  - name: app
    image: myapp:1.0
  - name: logging-sidecar
    image: vector:0.36
    volumeMounts:
    - name: logs
      mountPath: /var/log
  volumes:
  - name: logs
    emptyDir: {}
```

Both share the network — `localhost:8080` from sidecar reaches app.

## When NOT to use a Deployment

- **Stateful services** (databases) — use **StatefulSet** for stable network identity and per-pod volumes.
- **Per-node agents** (log collectors, metrics) — use **DaemonSet**.
- **One-off tasks** — use **Job** (or **CronJob** for scheduled).
