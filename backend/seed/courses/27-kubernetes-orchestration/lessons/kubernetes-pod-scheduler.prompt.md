# Pod Scheduling Feasibility Checker

Given a cluster description, determine whether a pod can be scheduled on each node. Apply the checks in this order:

1. **Label / nodeSelector check** — all pod selector key=value pairs must be present in the node's labels.
2. **Taint check** — every node taint with effect `NoSchedule` or `NoExecute` must be tolerated by the pod.
3. **Resource check** — the node must have enough CPU (millicores) and memory (MiB).

Report the **first** failing check. If all pass, report `SCHEDULABLE`.

## Input

```
Line 1: N (number of nodes, 1 <= N <= 10)
Next N lines: node_name cpu_milli mem_mib taint_count label_count [taint1 ...] [label1 ...]
  taints listed first, then labels
  taints format: key=value:NoSchedule  or  key=value:NoExecute
  labels format: key=value
Next line: pod_name cpu_milli mem_mib toleration_count selector_count [tol1 ...] [sel1 ...]
  tolerations listed first, then selectors
  tolerations format: key=value:NoSchedule  or  key=value:NoExecute
  selectors format: key=value
```

## Output

One line per node: `node_name STATUS`

Status is one of: `SCHEDULABLE`, `LABEL_MISMATCH`, `TAINT_NOT_TOLERATED`, `INSUFFICIENT_CPU`, `INSUFFICIENT_MEMORY`.

## Examples

Input:
```
3
node1 4000 8192 1 2 env=prod:NoSchedule tier=backend region=us
node2 500 1024 0 1 region=us
node3 2000 4096 0 2 tier=backend region=us
pod1 1000 2048 1 1 env=prod:NoSchedule tier=backend
```

Output:
```
node1 SCHEDULABLE
node2 LABEL_MISMATCH
node3 SCHEDULABLE
```

Input:
```
2
nodeA 200 512 0 1 app=web
nodeB 4000 8192 1 1 gpu=true:NoSchedule app=web
pod2 300 256 0 1 app=web
```

Output:
```
nodeA INSUFFICIENT_CPU
nodeB TAINT_NOT_TOLERATED
```

## Notes

- The pod tolerates a taint if it has a matching toleration with identical `(key, value, effect)`.
- Only `NoSchedule` and `NoExecute` taints block scheduling. `PreferNoSchedule` is ignored.
- Selectors must ALL match (AND semantics). Extra node labels are fine.
- On each node line: taints come before labels in the token stream.
- On the pod line: tolerations come before selectors in the token stream.
