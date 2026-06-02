# Horizontal Pod Autoscaler (HPA)

The **Horizontal Pod Autoscaler** automatically adjusts the number of pod replicas in a Deployment (or StatefulSet, ReplicaSet) based on observed metrics. It is the primary tool for handling variable load in Kubernetes.

## How HPA Works

HPA runs a control loop (default every 15 seconds) that:
1. Reads current metric values from the Metrics API.
2. Computes the desired replica count: `desiredReplicas = ceil(currentReplicas × (currentMetric / targetMetric))`.
3. Updates the target's `spec.replicas`.

## Prerequisites

- **metrics-server** must be installed for CPU/memory-based scaling.
- **Prometheus Adapter** or KEDA is needed for custom/external metrics.

## Basic CPU-Based HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60    # target 60% of CPU request
```

With 2 pods at 120% CPU utilization: `ceil(2 × 120/60) = 4` pods.

## Memory-Based Scaling

```yaml
  metrics:
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 400Mi
```

## Multiple Metrics

HPA takes the metric that requires the **most replicas** (conservative):

```yaml
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 400Mi
```

## Scale-Down Behavior (Stabilization)

To prevent thrashing (rapid scale-down after a brief traffic drop):

```yaml
spec:
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300   # wait 5 min before scaling down
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60              # scale down at most 50% per minute
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Pods
        value: 4
        periodSeconds: 60             # add at most 4 pods per minute
```

## Checking HPA Status

```bash
kubectl get hpa -n production
# NAME      REFERENCE         TARGETS   MINPODS   MAXPODS   REPLICAS
# api-hpa   Deployment/api    45%/60%   2         20        4

kubectl describe hpa api-hpa -n production   # events show scaling decisions
```

## Common Pitfalls

| Problem                         | Cause                                              |
|---------------------------------|----------------------------------------------------|
| HPA shows `<unknown>` metric    | metrics-server not installed or pod has no requests |
| Replicas stuck at min           | `averageUtilization` target too high               |
| Rapid scale-down/scale-up       | No stabilization window configured                 |
| HPA fights with manual scaling  | `kubectl scale` conflicts — let HPA own replicas  |

## KEDA — Event-Driven Autoscaling

KEDA (Kubernetes Event-Driven Autoscaling) extends HPA with 60+ scalers including Kafka lag, SQS queue depth, Redis, HTTP request rate, and more.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: worker-scaledobject
spec:
  scaleTargetRef:
    name: worker-deployment
  minReplicaCount: 0        # scale to zero!
  maxReplicaCount: 50
  triggers:
  - type: kafka
    metadata:
      topic: orders
      lagThreshold: "100"   # one replica per 100 messages of lag
```

KEDA can scale to **zero** when the queue is empty — impossible with native HPA.
