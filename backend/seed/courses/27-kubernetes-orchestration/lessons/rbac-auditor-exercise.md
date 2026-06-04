# Exercise: RBAC Permission Auditor

Kubernetes **RBAC** (Role-Based Access Control) is the gatekeeper for every API request. Before any change lands in etcd, the API server checks: does this subject (user, group, or ServiceAccount) have a Role or ClusterRole that grants the requested verb on the requested resource in the relevant namespace?

This exercise asks you to implement that authorization check.

## Key Concepts

- A **Role** grants permissions within a single namespace.
- A **ClusterRole** grants permissions across all namespaces (or for cluster-scoped resources like nodes).
- A **RoleBinding** attaches a Role (or ClusterRole) to subjects *within a namespace*.
- A **ClusterRoleBinding** attaches a ClusterRole to subjects *cluster-wide*.

**Critical:** Kubernetes Secrets are **not encrypted by default** — they are base64-encoded. RBAC is the primary access control mechanism preventing unauthorized reads of Secret objects.

> **Further reading:** [RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) in the official Kubernetes docs and the [CNCF CKA Curriculum](https://github.com/cncf/curriculum) which lists RBAC as a major exam domain.

See the exercise prompt for the full input/output specification.
