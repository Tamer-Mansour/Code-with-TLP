# Deployment Rolling Update Simulator

Simulate a Kubernetes Deployment rolling update.

Given an initial number of replicas (all running the old image), `maxSurge` (extra pods allowed above desired), and `maxUnavailable` (pods that can be unavailable during the rollout), simulate the rolling update step by step.

## Algorithm

Repeat until `old == 0`:
1. If `old > 0`: scale up new pods until `old + new == desired + maxSurge`.
2. Print the current state as `Step N: old=X new=Y total=Z`.
3. If `old == 0`: stop.
4. Kill old pods: remove up to `new - (desired - maxUnavailable)` old pods. Always remove at least 1 to guarantee progress.

After `old` reaches 0, print one final state line then `Rollout complete`.

## Input

A single line with three integers:

```
replicas maxSurge maxUnavailable
```

Constraints: `1 <= replicas <= 20`, `1 <= maxSurge <= 5`, `1 <= maxUnavailable <= 5`.

## Output

One line per step:

```
Step N: old=X new=Y total=Z
```

Followed by:

```
Rollout complete
```

## Examples

Input:
```
4 1 1
```

Output:
```
Step 1: old=4 new=1 total=5
Step 2: old=3 new=2 total=5
Step 3: old=2 new=3 total=5
Step 4: old=1 new=4 total=5
Step 5: old=0 new=4 total=4
Rollout complete
```

Input:
```
2 1 1
```

Output:
```
Step 1: old=2 new=1 total=3
Step 2: old=1 new=2 total=3
Step 3: old=0 new=2 total=2
Rollout complete
```

Input:
```
5 2 2
```

Output:
```
Step 1: old=5 new=2 total=7
Step 2: old=4 new=3 total=7
Step 3: old=3 new=4 total=7
Step 4: old=2 new=5 total=7
Step 5: old=0 new=5 total=5
Rollout complete
```

## Notes

- `maxSurge` and `maxUnavailable` are absolute pod counts (not percentages).
- New pods are assumed to become ready immediately for simulation purposes.
- The final step shows `new=desired` (not `desired+maxSurge`) because no more scale-up happens once `old` reaches 0.
- "Kill at least 1" guarantees the simulation terminates even when constraints are tight.
