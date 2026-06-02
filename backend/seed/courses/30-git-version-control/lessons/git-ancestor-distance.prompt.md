# Commit Ancestry Distance

You are given a commit graph as a directed acyclic graph (DAG). Each commit may have one or more parent commits. Your task is to find the **minimum number of edges (hops)** on the path from commit `A` to commit `B`, where `A` is always an ancestor of `B`.

## Input format

```
N
commit1 [parent1 parent2 ...]
commit2 [parent1 ...]
...
(one line per commit — the parent list may be empty for root commits)
A B
```

- First line: `N` — number of commits.
- Next `N` lines: each starts with a commit name, followed by zero or more parent names.
- Last line: two commit names `A` and `B`. `A` is guaranteed to be an ancestor of `B` (or equal to `B`).

## Output format

A single integer: the minimum number of hops from `A` to `B` (i.e., the length of the shortest path when traversing from child to parent).

## Example

**Input:**
```
4
A
B A
C B
D C
A D
```

**Output:**
```
3
```

Explanation: D → C → B → A, which is 3 hops.

## Constraints

- 1 ≤ N ≤ 1000
- Commit names are short alphanumeric strings.
- The graph is a valid DAG with no cycles.
- `A` is always a (possibly non-strict) ancestor of `B`.
