# Resource Management in Kubernetes

Every container in a Pod should declare its CPU and memory requirements. Without this information, the scheduler places pods blindly and nodes can become overloaded.

## Requests vs Limits

| Field      | Meaning                                                                 |
|------------|-------------------------------------------------------------------------|
| `requests` | The amount the scheduler reserves on a node. Affects placement.         |
| `limits`   | The maximum the container may use. CPU is throttled; memory triggers OOMKill. |

```yaml
resources:
  requests:
    cpu: "250m"       # 0.25 CPU cores
    memory: "128Mi"
  limits:
    cpu: "1"          # 1 full core
    memory: "512Mi"
```

`250m` means 250 millicores — one quarter of a CPU core. `Mi` is mebibytes (1 Mi = 1,048,576 bytes).

## Quality of Service Classes

K8s assigns a **QoS class** to each Pod, which determines eviction priority under memory pressure.

| QoS Class    | Condition                                       | Eviction Priority |
|--------------|-------------------------------------------------|--------------------|
| Guaranteed   | requests == limits for all containers           | Last evicted       |
| Burstable    | requests < limits (or only requests set)        | Middle             |
| BestEffort   | No requests or limits set                       | First evicted      |

For critical production workloads, use **Guaranteed** QoS (set requests == limits).

## LimitRange — Namespace Defaults

You can set default requests and limits for an entire namespace so developers don't have to think about it for every workload:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: production
spec:
  limits:
  - type: Container
    default:
      cpu: "500m"
      memory: "256Mi"
    defaultRequest:
      cpu: "100m"
      memory: "64Mi"
```

## ResourceQuota — Namespace Cap

A **ResourceQuota** limits the total resources consumed across all Pods in a namespace:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: team-a
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 4Gi
    limits.cpu: "8"
    limits.memory: 8Gi
    pods: "20"
```

## Practical Guidelines

- **Always set requests.** The scheduler needs them for correct placement.
- **Set limits for memory** to cap OOM impact. Be conservative but not too tight — an OOMKilled pod reveals itself fast.
- **Be careful with CPU limits.** CPU throttling can hurt tail latency without the pod appearing unhealthy. Consider omitting CPU limits if latency matters, but keep requests.
- **Monitor actual usage** with `kubectl top pods` (requires metrics-server) and tune over time.

```bash
kubectl top pods -n production
kubectl top nodes
kubectl describe node <node-name> | grep -A8 Allocated
```

## Vertical Pod Autoscaler (VPA)

VPA automatically recommends or sets resource requests based on observed usage:

```bash
kubectl describe vpa my-app -n production
# Shows: Lower Bound / Target / Upper Bound recommendations
```

VPA is complementary to HPA (Horizontal Pod Autoscaler). Use HPA for stateless scaling; use VPA recommendations to tune your base requests.
