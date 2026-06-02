# RBAC in Kubernetes

**Role-Based Access Control (RBAC)** governs who can do what in a Kubernetes cluster. Every `kubectl` command, every CI/CD pipeline, and every Pod that calls the API server is subject to RBAC.

## The Four Objects

| Object              | Scope       | Purpose                                              |
|---------------------|-------------|------------------------------------------------------|
| Role                | Namespace   | Defines allowed API operations within a namespace    |
| ClusterRole         | Cluster     | Like Role but cluster-wide (also used for non-namespaced resources) |
| RoleBinding         | Namespace   | Binds a Role (or ClusterRole) to subjects in a namespace |
| ClusterRoleBinding  | Cluster     | Binds a ClusterRole to subjects cluster-wide         |

## Subjects

A subject is the entity being granted permissions:
- **User** — a human user (managed externally; K8s has no user store).
- **Group** — a set of users.
- **ServiceAccount** — an identity for a Pod or process running inside the cluster.

## Role Example

Allow reading pods and logs in the `production` namespace:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
- apiGroups: [""]           # "" = core API group
  resources: [pods, pods/log]
  verbs: [get, list, watch]
```

## RoleBinding Example

Grant the `pod-reader` Role to a CI service account:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ci-pod-reader
  namespace: production
subjects:
- kind: ServiceAccount
  name: ci-runner
  namespace: ci
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

## ServiceAccount for Pods

When a Pod needs to call the K8s API (e.g., an operator or a monitoring agent):

```yaml
# 1. Create the ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: metrics-collector
  namespace: monitoring

# 2. Bind a ClusterRole (e.g., viewing nodes and pods)
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: metrics-collector-binding
subjects:
- kind: ServiceAccount
  name: metrics-collector
  namespace: monitoring
roleRef:
  kind: ClusterRole
  name: view               # built-in read-only role
  apiGroup: rbac.authorization.k8s.io
```

```yaml
# 3. Reference in Pod spec
spec:
  serviceAccountName: metrics-collector
```

The Pod automatically receives a mounted token it can use to authenticate against the API server.

## Common Built-in ClusterRoles

| ClusterRole          | Allows                                        |
|----------------------|-----------------------------------------------|
| `cluster-admin`      | Full access to everything. Use sparingly.     |
| `admin`              | Namespace-scoped admin (cannot manage RBAC itself) |
| `edit`               | Create/update/delete most resources           |
| `view`               | Read-only access                              |

## Debugging RBAC

```bash
# Can a serviceaccount list pods?
kubectl auth can-i list pods \
  --as=system:serviceaccount:monitoring:metrics-collector \
  -n production

# See effective permissions for current user
kubectl auth can-i --list -n production

# Describe a RoleBinding
kubectl describe rolebinding ci-pod-reader -n production
```

## Principle of Least Privilege

- Grant only the verbs and resources a subject truly needs.
- Prefer `Role` + `RoleBinding` (namespace-scoped) over `ClusterRole` + `ClusterRoleBinding`.
- Avoid giving `*` verbs or `*` resources — it is effectively cluster-admin.
- Rotate ServiceAccount tokens with `automountServiceAccountToken: false` on pods that don't need API access.
