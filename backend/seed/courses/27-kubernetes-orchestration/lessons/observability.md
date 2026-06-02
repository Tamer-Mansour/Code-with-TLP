# Observability in Kubernetes

Running workloads in Kubernetes without observability is flying blind. Three pillars — **logs**, **metrics**, and **traces** — give you visibility into what is happening inside your cluster.

## Logs

Every container writes to stdout/stderr. K8s captures these and exposes them via `kubectl logs`.

```bash
kubectl logs deploy/api -n production                  # latest pod
kubectl logs deploy/api -n production -f               # follow (tail -f)
kubectl logs deploy/api -n production --previous       # crashed container
kubectl logs -l app=api -n production --all-containers # all matching pods
```

For persistent log aggregation, deploy a DaemonSet log shipper:

- **Fluentd / Fluent Bit** — collect from `/var/log/containers/`, ship to Elasticsearch, Loki, or CloudWatch.
- **Vector** — high-performance Rust-based alternative.
- **Grafana Loki** — lightweight log aggregation; pairs well with Prometheus.

## Metrics

**metrics-server** provides basic CPU and memory usage for `kubectl top`:

```bash
kubectl top pods -n production
kubectl top nodes
```

For full metrics, deploy **Prometheus** + **Grafana**. The `kube-prometheus-stack` Helm chart bundles everything:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prom prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace
```

This deploys:
- Prometheus — scrapes metrics from pods (via `ServiceMonitor` CRDs).
- Alertmanager — routes alerts to Slack, PagerDuty, email.
- Grafana — dashboards. Default dashboards include node, pod, and cluster views.

### Exposing Application Metrics

Add a `/metrics` endpoint (Prometheus exposition format) and annotate the Service:

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
    prometheus.io/path: "/metrics"
```

Or create a `ServiceMonitor` CRD if using the Prometheus Operator.

## Key Cluster Metrics to Watch

| Metric                                | Alert When...                        |
|---------------------------------------|--------------------------------------|
| `node_memory_MemAvailable_bytes`      | < 10% of total memory                |
| `container_cpu_usage_seconds_total`   | Consistently near CPU limit          |
| `kube_pod_container_status_restarts_total` | Increasing rapidly (crash loop) |
| `kubelet_volume_stats_available_bytes` | < 20% of PVC capacity               |
| `kube_deployment_status_replicas_unavailable` | > 0 for extended time       |

## Events

K8s events record cluster activity and are invaluable for debugging:

```bash
kubectl get events -n production --sort-by='.lastTimestamp'
kubectl describe pod web-abc -n production   # events at the bottom
```

Events are ephemeral (deleted after ~1 hour by default). For persistent event storage, deploy **Event Exporter** or **kube-event-exporter** to ship events to your log aggregation system.

## Distributed Tracing

For request-level tracing across microservices, instrument your apps with **OpenTelemetry** SDKs and collect with:

- **Jaeger** — open-source; good for getting started.
- **Tempo** (Grafana) — integrates with Loki and Prometheus in the Grafana stack.
- **AWS X-Ray / Google Cloud Trace** — managed options on cloud platforms.

The Kubernetes networking itself is transparent to traces — your app propagates trace context (W3C TraceContext headers) between services.

## A Minimal Observability Stack

```
Metrics:  kube-prometheus-stack (Prometheus + Grafana + Alertmanager)
Logs:     Fluent Bit (DaemonSet) → Grafana Loki → Grafana
Traces:   OpenTelemetry Collector + Grafana Tempo
```

All three displayed together in Grafana give a unified view of your cluster's health.
