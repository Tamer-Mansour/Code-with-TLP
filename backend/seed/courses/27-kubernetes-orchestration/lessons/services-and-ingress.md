# Services and Ingress

Pods come and go. Their IPs change. **Services** give a stable virtual IP + DNS name that load-balances to whichever pods match a label selector.

## ClusterIP — internal

The default. Routable only inside the cluster.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector: { app: web }
  ports:
  - port: 80          # service port
    targetPort: 80    # container port
```

Now `web` (in the same namespace) or `web.default.svc.cluster.local` (fully qualified) resolves to the service's virtual IP, which round-robins to pods with `app=web`.

## NodePort — exposed on every node

```yaml
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080
```

Reachable at `nodeIP:30080`. Convenient for dev clusters; awkward for prod.

## LoadBalancer — cloud-provisioned LB

```yaml
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
```

On AWS/GCP/Azure this provisions a real load balancer with a public IP. Each LB costs money — usually you put **one Ingress** in front of many services instead.

## ExternalName — DNS alias

```yaml
spec:
  type: ExternalName
  externalName: my.legacy.api.example.com
```

`web` in cluster resolves to that external hostname. Useful for gradual migrations.

## Ingress — HTTP/HTTPS routing

An Ingress is a layer-7 router for the cluster. One Ingress, one cloud LB, many services routed by host/path.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts: [api.example.com]
    secretName: api-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: api-v1
            port: { number: 80 }
      - path: /v2
        pathType: Prefix
        backend:
          service:
            name: api-v2
            port: { number: 80 }
```

You need an **Ingress controller** running in the cluster: nginx-ingress, Traefik, HAProxy, or the cloud's own (AWS ALB Controller, GCP GCLB).

## Gateway API — the replacement

The newer **Gateway API** (`Gateway` + `HTTPRoute`) is gradually replacing Ingress. More features, cleaner separation of concerns. For greenfield clusters, prefer Gateway API.

## Service mesh (when you need it)

Istio, Linkerd, Cilium service mesh. They add:

- **mTLS** between services automatically.
- **Fine-grained routing** (canary, A/B).
- **Observability** — per-service metrics, traces.
- **Resilience** — retries, circuit breakers, timeouts at the proxy.

Cost: complexity. Don't add a mesh unless you have several teams operating dozens of services.

## Common networking pitfalls

- Service `port` ≠ container `targetPort` — set both, even if equal.
- Pods on different namespaces need fully-qualified DNS or NetworkPolicy.
- `LoadBalancer` services in cloud cost real money — consolidate behind Ingress.
- `NodePort` exposes on every node — be sure your firewall is correct.
