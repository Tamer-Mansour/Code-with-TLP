# Scheduling, Resource Management, and Autoscaling

The Kubernetes **scheduler** is responsible for one decision: given a pending pod, which node should it run on? It never creates pods — that is the job of controllers like the ReplicaSet controller. It only writes the `nodeName` field on a pod, then the kubelet on that node takes over.

## How the Scheduler Works

The scheduler runs a two-phase algorithm for each pending pod:

1. **Filtering** — eliminate nodes that cannot run the pod (insufficient CPU, memory, or a taint the pod does not tolerate, or a required label the node does not have).
2. **Scoring** — rank the remaining nodes (prefer nodes with more free resources, spread pods across failure domains, etc.).

The node with the highest score wins.

## Resource Requests vs Limits

```yaml
containers:
- name: api
  image: api:1.0
  resources:
    requests:
      cpu: "250m"      # 0.25 CPU cores — used for scheduling decisions
      memory: "256Mi"  # used for scheduling decisions
    limits:
      cpu: "1000m"     # throttled if exceeded (CPU is compressible)
      memory: "512Mi"  # OOMKilled if exceeded (memory is incompressible)
```

- **Requests** are what the scheduler uses to find a node with enough headroom.
- **Limits** cap runtime usage. Exceeding a CPU limit causes throttling. Exceeding a memory limit causes the container to be OOM-killed.
- A pod with no requests is treated as `requests: 0` for scheduling but receives `BestEffort` QoS — it is the first to be evicted under node pressure.

## Node Affinity

Require or prefer specific node characteristics:

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: topology.kubernetes.io/zone
          operator: In
          values: [us-east-1a, us-east-1b]
```

`requiredDuring...` is a hard filter (pod stays unscheduled if no match). `preferredDuring...` is a soft preference (scheduler tries but does not block).

## Taints and Tolerations

Taints on nodes **repel** pods. Tolerations on pods **opt in** to tainted nodes.

```bash
# Taint a node (only GPU pods should land here)
kubectl taint nodes gpu-node-1 accelerator=nvidia:NoSchedule
```

```yaml
# Pod toleration
tolerations:
- key: accelerator
  value: nvidia
  effect: NoSchedule
```

Effects:
- `NoSchedule` — new pods without the toleration won't be scheduled.
- `PreferNoSchedule` — soft version of NoSchedule.
- `NoExecute` — existing pods without the toleration are evicted.

## LimitRanges and ResourceQuotas

**LimitRange** sets default requests/limits and min/max bounds per container within a namespace:

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
      memory: "128Mi"
    max:
      cpu: "2"
      memory: "1Gi"
```

**ResourceQuota** caps total consumption across all pods in a namespace:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: production
spec:
  hard:
    requests.cpu: "10"
    requests.memory: "20Gi"
    pods: "50"
```

## Horizontal Pod Autoscaler (HPA)

HPA scales the replica count of a Deployment or StatefulSet based on metrics. The core formula is:

```
desiredReplicas = ceil(currentReplicas × (currentMetric / targetMetric))
```

**Important correction:** HPA reads CPU and memory from the **Metrics Server** (`metrics.k8s.io` API), *not* from Prometheus. Prometheus is a separate monitoring system. Metrics Server is a lightweight aggregator designed specifically for the HPA and `kubectl top` commands.

## Vertical Pod Autoscaler (VPA) and Cluster Autoscaler

- **VPA** recommends or automatically adjusts the resource requests/limits of individual containers based on observed usage.
- **Cluster Autoscaler** adds or removes nodes from the node pool when pods are unschedulable (due to resource constraints) or nodes are underutilized.

## KEDA — Event-Driven Autoscaling

KEDA extends HPA with 60+ external scalers (Kafka, SQS, Redis, etc.) and enables scaling to **zero** replicas when there is no work to do — something native HPA cannot achieve.

> **Further reading:** [Kubernetes Scheduling docs](https://kubernetes.io/docs/concepts/scheduling-eviction/) and [A Guide to Kubernetes for SREs and Sysadmins](https://opensource.com/downloads/kubernetes-sysadmin) cover scheduling and resource management from an operations perspective.
