# Kubernetes Production Best Practices

Running Kubernetes in production is very different from running it locally. This lesson collects the highest-impact practices for reliability, security, and cost efficiency.

## Workload Reliability

**Set resource requests and limits on every container.**
Without requests, the scheduler places pods arbitrarily. Without limits, a misbehaving pod can OOM the node.

**Define readiness and liveness probes.**
K8s cannot make smart routing or restart decisions without them.

**Use at least 2 replicas for any stateless service.**
One replica means a single node failure takes your service down. Set `minReplicas: 2` on HPA as well.

**Configure Pod Disruption Budgets (PDB).**
Prevent maintenance operations from taking down too many replicas at once:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
  namespace: production
spec:
  minAvailable: 2       # or maxUnavailable: 1
  selector:
    matchLabels:
      app: api
```

**Use `RollingUpdate` with `maxUnavailable: 0`.**
Guarantees zero downtime during deployments.

## Security Hardening

**Run containers as non-root:**

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: [ALL]
```

**Scan images for vulnerabilities** before pushing to production. Tools: Trivy, Snyk, Grype.

**Use NetworkPolicies** to enforce least-privilege network access between pods.

**Restrict RBAC to minimum required permissions.** Avoid `cluster-admin` for application workloads.

**Never store secrets in ConfigMaps or environment variables committed to Git.** Use the External Secrets Operator or HashiCorp Vault.

## Cost Efficiency

| Practice                          | Impact                                 |
|-----------------------------------|----------------------------------------|
| Set accurate resource requests     | Avoids over-provisioning nodes         |
| Use HPA + Cluster Autoscaler      | Scale nodes in/out with demand         |
| Use spot/preemptible nodes        | 60-90% cheaper; tolerate evictions     |
| Scale-to-zero with KEDA            | Zero cost when workload is idle        |
| Delete unused namespaces/PVCs     | Idle PVCs cost money                   |

## Namespace Strategy

Organize by team or environment. Typical setup:

```
production/      # live traffic
staging/         # pre-prod testing
dev/             # developer sandbox
monitoring/      # observability stack
```

Apply **ResourceQuotas** and **LimitRanges** per namespace so one team cannot starve another.

## Image Management

- **Pin image tags** to a specific SHA or immutable tag (`v1.2.3`). Never use `latest` in production.
- Use **private registries** and configure `imagePullSecrets`.
- Set **ImagePullPolicy: IfNotPresent** to avoid re-pulling the same tag.

## Cluster Upgrade Strategy

1. Upgrade the control plane first (managed clusters do this for you).
2. Drain and upgrade worker nodes one at a time (or use node groups).
3. Never skip minor versions (go 1.28 → 1.29 → 1.30, not 1.28 → 1.30).
4. Test workloads in staging on the new version first.
5. Check for deprecated API versions before upgrading (`kubectl api-versions`).

```bash
# Check for deprecated APIs in your manifests
kubectl convert -f manifests/ --output-version apps/v1   # deprecated in newer K8s
```

## Checklist

- [ ] All containers have `resources.requests` and `resources.limits`
- [ ] All services have `readinessProbe` and `livenessProbe`
- [ ] Deployments have `minAvailable` PDB
- [ ] Containers run as non-root with `readOnlyRootFilesystem`
- [ ] No secrets in ConfigMaps or plain env vars
- [ ] NetworkPolicies restrict east-west traffic
- [ ] HPA configured with stable scale-down behavior
- [ ] Image tags pinned to specific versions
- [ ] Cluster nodes running within N-1 of latest K8s minor version
