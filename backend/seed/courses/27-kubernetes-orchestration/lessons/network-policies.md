# Network Policies

By default, every Pod in a Kubernetes cluster can talk to every other Pod. **NetworkPolicy** resources let you restrict this to only the traffic you explicitly allow — a form of micro-segmentation.

## How NetworkPolicy Works

A NetworkPolicy selects Pods via label selectors and defines ingress and/or egress rules. Only CNI plugins that support NetworkPolicy enforce them (Calico, Cilium, Weave). Flannel does not — check your CNI.

## Default-Deny All Ingress

A common baseline: deny all incoming traffic to a namespace, then add policies to allow only what is needed.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}          # selects ALL pods in namespace
  policyTypes: [Ingress]
  # no ingress rules = deny all
```

## Allow Traffic from a Specific Namespace

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-monitoring
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes: [Ingress]
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: monitoring
    ports:
    - protocol: TCP
      port: 9090
```

## Allow Frontend to Reach Backend Only

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow-frontend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes: [Ingress]
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

## Egress Restriction

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes: [Egress]
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - ports:                 # allow DNS
    - protocol: UDP
      port: 53
```

**Always allow UDP port 53** in egress policies — otherwise DNS resolution breaks.

## Key Rules Reference

| Field              | Selects                                      |
|--------------------|----------------------------------------------|
| `podSelector: {}`  | All pods in the policy's namespace           |
| `podSelector: {matchLabels: ...}` | Pods with specific labels     |
| `namespaceSelector` | Pods in matching namespaces                 |
| `ipBlock`          | CIDR ranges (useful for external IPs)        |

## Testing a Policy

```bash
# Verify a pod CAN reach its allowed destination
kubectl exec -n production deploy/frontend -- curl -s http://api:8080/health

# Verify a pod CANNOT reach a denied service
kubectl exec -n production deploy/api -- curl --max-time 3 http://postgres:5432
# Should time out
```

NetworkPolicies are additive — multiple policies selecting the same pod union their rules. There is no explicit "deny" rule beyond the implicit deny created by the policy's existence.
