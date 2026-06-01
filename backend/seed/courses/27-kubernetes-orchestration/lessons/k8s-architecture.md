# Kubernetes Architecture

Kubernetes ("K8s") is a container orchestration platform. You declare what you want running; K8s figures out how to schedule, restart, scale, and connect it.

## The two halves of a cluster

```
┌──────────────────────────────┐         ┌──────────────────────────────┐
│      CONTROL PLANE           │         │       WORKER NODES           │
│  ┌─────────────┐             │         │  ┌─────────────┐             │
│  │ kube-apiserver │           │◄────────│  │ kubelet     │             │
│  └─────────────┘             │         │  │ container   │             │
│  ┌─────────────┐  ┌─────────┐ │         │  │  runtime    │             │
│  │ scheduler   │  │ etcd    │ │         │  │ kube-proxy  │             │
│  └─────────────┘  └─────────┘ │         │  └─────────────┘             │
│  ┌─────────────────────────┐ │         │  ┌─────────────┐             │
│  │ controller-manager      │ │         │  │  POD POD POD│             │
│  └─────────────────────────┘ │         │  └─────────────┘             │
└──────────────────────────────┘         └──────────────────────────────┘
```

### Control plane

- **kube-apiserver** — REST API everyone talks to.
- **etcd** — consistent KV store; the cluster's source of truth.
- **scheduler** — decides which node a new pod runs on.
- **controller-manager** — runs the reconciliation loops (Deployment, ReplicaSet, etc.).
- **cloud-controller-manager** — talks to your cloud (load balancers, volumes).

### Worker node

- **kubelet** — agent that ensures the containers asked for are running.
- **container runtime** — containerd, CRI-O. Actually runs containers.
- **kube-proxy** — implements Services networking.

## Declarative model

You don't tell K8s "create a pod here." You **declare** what you want:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels: { app: web }
  template:
    metadata:
      labels: { app: web }
    spec:
      containers:
      - name: web
        image: ghcr.io/me/web:1.2.3
        ports: [ { containerPort: 80 } ]
```

K8s sees: "Deployment named `web` wants 3 replicas." It creates the ReplicaSet, which creates Pods, which the scheduler places on nodes. If a pod dies, the controller notices the gap and creates a new one. Forever.

## Resources you'll meet

| Object              | Purpose                                       |
|---------------------|-----------------------------------------------|
| Pod                 | One or more containers, scheduled together    |
| Deployment          | Manages a ReplicaSet, handles rolling updates |
| ReplicaSet          | Maintains N copies of a Pod                   |
| StatefulSet         | Pods with stable identity + storage           |
| DaemonSet           | One pod per node                              |
| Job / CronJob       | Run-to-completion / scheduled                 |
| Service             | Stable virtual IP + DNS for a set of pods     |
| Ingress             | HTTP/HTTPS routing into the cluster           |
| ConfigMap           | Non-secret config                             |
| Secret              | Sensitive config                              |
| PersistentVolume    | Storage backing                               |
| Namespace           | Tenant boundary                               |

## Where to run K8s

- **Cloud managed**: EKS, GKE, AKS, DigitalOcean K8s. The right default.
- **Local for dev**: `kind`, `minikube`, k3d, Docker Desktop K8s.
- **Self-managed prod**: kubeadm, k3s, RKE2. Lots of work — only if regulatory requires it.

For learning: install `kubectl`, then spin up a local cluster with `kind create cluster`.

## The cost / complexity warning

K8s is powerful and operationally heavy. For a single service you'd never grow beyond a few VMs, **don't use K8s**. Cloud Run, ECS Fargate, Fly.io, Render, even a systemd unit are simpler.

K8s makes sense when:
- You have 5+ services that need orchestration.
- You need to standardize deployments across many teams.
- You want portability across clouds.
- Your scale needs hundreds of containers and auto-scaling.
