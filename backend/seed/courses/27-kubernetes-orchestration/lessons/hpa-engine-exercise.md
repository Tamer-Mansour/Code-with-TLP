# Exercise: HPA Scaling Decision Engine

The Horizontal Pod Autoscaler runs a control loop every 15 seconds. At each tick it reads the current metric value and applies the formula:

```
desiredReplicas = ceil(currentReplicas × (currentMetric / targetMetric))
```

The result is clamped to `[minReplicas, maxReplicas]`. However, to prevent **thrashing** (oscillating scale-up and scale-down), the HPA enforces cooldown periods:

- **Scale-up cooldown:** 3 minutes (180 seconds) must elapse since the last scaling event before another scale-up is allowed.
- **Scale-down cooldown:** 5 minutes (300 seconds) must elapse since the last scaling event before a scale-down is allowed.

In this exercise you simulate the HPA controller processing a sequence of metric observations.

> **Important correction:** HPA reads CPU/memory metrics from the **Metrics Server** (`metrics.k8s.io`), NOT from Prometheus. Prometheus is used for alerting and dashboards. Metrics Server is a lightweight aggregator purpose-built for the HPA and `kubectl top` commands. Using Prometheus for basic HPA would require installing the Prometheus Adapter as a separate component.

> **Further reading:** [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) in the official docs and [CNCF CKA Curriculum](https://github.com/cncf/curriculum) which includes autoscaling as a core exam topic.

See the exercise prompt for the full input/output specification.
