# Kubernetes Networking

Kubernetes networking follows four rules that every implementation must satisfy:

1. Every Pod gets its own IP address.
2. Pods can communicate with any other Pod without NAT.
3. Nodes can communicate with Pods without NAT.
4. The IP a Pod sees itself as is the same IP others see.

This is called the **flat network model**.

## Pod-to-Pod Communication

When two Pods are on the same node they communicate through a virtual bridge. When on different nodes, a CNI (Container Network Interface) plugin routes packets between nodes.

Popular CNI plugins:

| Plugin   | Notes                                               |
|----------|-----------------------------------------------------|
| Flannel  | Simple, overlay-based, good for small clusters      |
| Calico   | BGP-based, supports NetworkPolicy, widely used      |
| Cilium   | eBPF-powered, high performance, rich observability  |
| Weave    | Simple setup, supports encryption                   |

You don't usually pick a CNI yourself — managed K8s (EKS, GKE, AKS) installs one for you.

## DNS in the Cluster

Every Service gets a DNS name: `<service>.<namespace>.svc.cluster.local`.

```bash
# From inside any pod, these all resolve to the same Service:
curl http://api                          # same namespace
curl http://api.production              # short form
curl http://api.production.svc.cluster.local  # full FQDN
```

CoreDNS handles name resolution inside the cluster. It runs as a Deployment in the `kube-system` namespace.

```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

## Service Types

| Type          | Accessibility                                       |
|---------------|-----------------------------------------------------|
| ClusterIP     | Cluster-internal only (default)                     |
| NodePort      | Exposed on every node at a static port (30000–32767)|
| LoadBalancer  | Cloud creates an external load balancer             |
| ExternalName  | Alias for an external DNS name (no proxy)           |

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 8080
```

`port` is the Service port; `targetPort` is the container port.

## kube-proxy and iptables

`kube-proxy` runs on every node and programs iptables (or IPVS) rules that redirect traffic to a Service's virtual IP toward one of the healthy Pod IPs (endpoints). It watches the API server for Endpoint changes and updates rules immediately.

## Headless Services

Set `clusterIP: None` to get a "headless" Service — DNS returns all Pod IPs individually instead of a virtual IP. Used by StatefulSets so each Pod is DNS-addressable by name.

```yaml
spec:
  clusterIP: None
  selector:
    app: postgres
```

`postgres-0.postgres.production.svc.cluster.local` resolves to the first pod.

## Debugging Network Issues

```bash
# Check endpoints (are pods being selected?)
kubectl get endpoints api -n production

# Run a temporary debug pod
kubectl run netdebug --image=nicolaka/netshoot -it --rm -- bash

# From inside the debug pod:
curl http://api.production/health
nslookup api.production.svc.cluster.local
```

If `kubectl get endpoints` shows `<none>`, your Service selector does not match any Pod labels.
