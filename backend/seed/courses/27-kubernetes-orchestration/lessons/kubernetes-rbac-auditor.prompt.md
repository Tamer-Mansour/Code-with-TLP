# RBAC Permission Auditor

Given a set of RBAC Role definitions and RoleBindings, determine whether a given user can perform a specific action on a specific resource in a given namespace.

## Rules

- **Roles** define `(namespace, role_name, resource, verbs[])`. Use namespace `*` for a ClusterRole.
- **RoleBindings** bind `(namespace, role_name)` to a user. Use binding_namespace `*` for a ClusterRoleBinding (references a ClusterRole with namespace `*`).
- A ClusterRoleBinding (`binding_namespace = *`) grants the ClusterRole's permissions in **all** namespaces.
- A RoleBinding (`binding_namespace = specific_ns`) grants permissions only in that namespace.
- Permissions are **additive** — if any binding path grants the verb, the answer is `ALLOWED`.

## Input

```
Line 1: R B Q   (number of roles, bindings, queries)
Next R lines: namespace role_name resource verb_count verb1 verb2 ...
Next B lines: binding_namespace role_name user
  (use * for binding_namespace to mean ClusterRoleBinding, paired with a role whose namespace is also *)
Next Q lines: user verb resource namespace
```

## Output

One line per query: `ALLOWED` or `DENIED`.

## Examples

Input:
```
4 3 4
default dev-role pods 3 get list watch
default dev-role deployments 2 get list
kube-system admin-role secrets 1 get
* cluster-reader nodes 2 get list
default dev-role alice
kube-system admin-role bob
* cluster-reader alice
alice get pods default
alice delete pods default
bob get secrets kube-system
alice get nodes default
```

Output:
```
ALLOWED
DENIED
ALLOWED
ALLOWED
```

Input:
```
3 2 3
staging viewer pods 2 get list
staging viewer services 1 get
* cluster-viewer pods 2 get list
staging viewer carol
* cluster-viewer carol
carol get pods staging
carol get pods production
carol delete pods staging
```

Output:
```
ALLOWED
ALLOWED
DENIED
```

Explanation for input 2:
- carol has a RoleBinding in `staging` for `viewer` (grants pod/service reads in staging).
- carol has a ClusterRoleBinding for `cluster-viewer` (grants pod reads everywhere).
- `carol get pods staging` → ALLOWED via either binding.
- `carol get pods production` → ALLOWED via ClusterRoleBinding (cluster-viewer covers all namespaces).
- `carol delete pods staging` → DENIED (no binding grants the `delete` verb).

## Notes

- A ClusterRoleBinding (`binding_ns = *`) looks up a role whose `namespace = *`.
- A RoleBinding (`binding_ns = foo`) looks up a role whose `namespace = foo`.
- There are no `deny` rules — Kubernetes RBAC is purely additive.
