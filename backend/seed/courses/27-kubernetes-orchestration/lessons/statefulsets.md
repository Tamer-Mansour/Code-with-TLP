# StatefulSets

A **StatefulSet** manages Pods that need stable identities — a predictable name, a stable network hostname, and per-pod persistent storage. Databases, message brokers, and distributed systems like Kafka or Zookeeper are classic use cases.

## StatefulSet vs Deployment

| Feature                      | Deployment       | StatefulSet                        |
|------------------------------|------------------|------------------------------------|
| Pod names                    | Random suffix    | Ordinal: `app-0`, `app-1`, `app-2` |
| Pod DNS                      | Service VIP      | Per-pod: `app-0.<headless-svc>`    |
| PVC per pod                  | Shared PVC only  | `volumeClaimTemplates` creates one PVC per pod |
| Scaling order                | Parallel         | Sequential (0→1→2 on scale-up)     |
| Deletion order               | Any order        | Reverse ordinal (2→1→0)            |

## Minimal StatefulSet Example

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres          # must match headless Service
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels: { app: postgres }
    spec:
      containers:
      - name: postgres
        image: postgres:16
        env:
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ReadWriteOnce]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 50Gi
```

K8s creates `data-postgres-0`, `data-postgres-1`, `data-postgres-2` PVCs — one per Pod.

## Required Headless Service

StatefulSets need a **headless Service** (clusterIP: None) so each Pod gets its own DNS record:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  clusterIP: None
  selector: { app: postgres }
  ports:
  - port: 5432
```

DNS records: `postgres-0.postgres.production.svc.cluster.local`, etc.

## Update Strategies

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 1    # only update pods with index >= 1 (canary pattern)
```

Setting `partition: 1` updates `postgres-2`, `postgres-1` but leaves `postgres-0` untouched — useful for staged rollouts.

## Scaling Considerations

```bash
kubectl scale statefulset postgres --replicas=5   # adds postgres-3, postgres-4
kubectl scale statefulset postgres --replicas=2   # removes postgres-4, postgres-3 (reverse order)
```

Scaling down does **not** delete PVCs. You must delete them manually if you want to reclaim storage. This is intentional — protecting data.

## When NOT to Use StatefulSet

- Read replicas behind a load balancer with no per-instance state → Deployment.
- Any workload where pods are truly interchangeable → Deployment.

Prefer managed database services (RDS, Cloud SQL) over running stateful workloads in K8s unless you have a compelling reason.
