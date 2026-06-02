# DaemonSets and Jobs

Two specialized workload controllers cover patterns that Deployments and StatefulSets cannot: running exactly one Pod per node, and running tasks to completion.

## DaemonSet

A **DaemonSet** ensures one Pod runs on every (or selected) node. When a new node joins the cluster, the DaemonSet schedules a Pod on it automatically.

**Typical uses:**
- Log collectors (Fluentd, Filebeat, Vector)
- Node metrics agents (Prometheus node-exporter)
- Network plugins (CNI agents, kube-proxy itself)
- Security agents (Falco, Wazuh)

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels: { app: node-exporter }
    spec:
      hostNetwork: true          # shares node network namespace
      hostPID: true              # sees node processes
      containers:
      - name: node-exporter
        image: prom/node-exporter:v1.8.1
        ports:
        - containerPort: 9100
          hostPort: 9100
```

### Run on Selected Nodes Only

Use `nodeSelector` or `nodeAffinity` to target a subset:

```yaml
spec:
  template:
    spec:
      nodeSelector:
        role: gpu-worker
```

## Job

A **Job** runs one or more Pods to completion. The Job succeeds when the required number of completions is reached.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate
spec:
  completions: 1
  parallelism: 1
  backoffLimit: 3             # retry up to 3 times on failure
  template:
    spec:
      restartPolicy: OnFailure   # Never or OnFailure
      containers:
      - name: migrate
        image: myapp:2.0
        command: ["python", "manage.py", "migrate"]
```

### Parallel Jobs

```yaml
spec:
  completions: 10             # run 10 tasks total
  parallelism: 3              # 3 at a time
```

K8s tracks how many completions have succeeded and schedules more pods until `completions` is met.

## CronJob

A **CronJob** creates a Job on a schedule (standard cron syntax).

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-report
spec:
  schedule: "0 2 * * *"          # 02:00 every day (UTC)
  concurrencyPolicy: Forbid      # don't start if previous still running
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: report
            image: myapp:2.0
            command: ["python", "generate_report.py"]
```

### concurrencyPolicy Options

| Value    | Behaviour                                      |
|----------|------------------------------------------------|
| Allow    | Run jobs concurrently (default)                |
| Forbid   | Skip new job if previous still running         |
| Replace  | Cancel running job and start a new one         |

## Quick Reference

```bash
kubectl get jobs                                  # list jobs
kubectl logs job/db-migrate                       # job pod logs
kubectl get cronjobs                              # list cronjobs
kubectl create job manual-run --from=cronjob/nightly-report  # trigger manually
kubectl delete job db-migrate                     # clean up
```
