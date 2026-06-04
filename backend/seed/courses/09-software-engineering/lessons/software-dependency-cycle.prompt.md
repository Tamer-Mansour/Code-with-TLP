# Dependency Graph Cycle Detector

Circular dependencies between software modules violate good coupling principles and make code hard to test and maintain.

Given a directed dependency graph (edge A → B means A depends on B), determine whether any cycle exists.

- **Cycle found:** print `CYCLE DETECTED` then one cycle as space-separated module names (starting and ending at the same node).
- **No cycle:** print `NO CYCLE` then a valid topological order (dependencies before dependents), space-separated.

## Input Format

```
N M
module_1
...
module_N
A B
...
```

- Line 1: `N` modules, `M` edges
- Next `N` lines: module names
- Next `M` lines: `A B` means A depends on B

## Output Format

No cycle:
```
NO CYCLE
auth config database utils
```

Cycle found:
```
CYCLE DETECTED
auth database auth
```

## Example

**Input:**
```
4 3
auth
database
utils
config
auth database
database utils
auth config
```

**Output:**
```
NO CYCLE
auth config database utils
```
