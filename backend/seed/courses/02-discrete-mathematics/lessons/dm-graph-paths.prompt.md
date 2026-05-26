# Count Paths in a DAG

## Problem

Given a directed acyclic graph (DAG) with `N` vertices (numbered 1 to N) and `M` directed edges, count the number of distinct paths from vertex `1` to vertex `N`.

A path is a sequence of vertices `v₁, v₂, ..., vₖ` where each `(vᵢ, vᵢ₊₁)` is a directed edge, `v₁ = 1`, and `vₖ = N`, with no repeated vertices (guaranteed by the DAG property).

## Input Format

```
N M
u₁ v₁
u₂ v₂
...
uₘ vₘ
```

First line: two integers N (vertices) and M (edges).
Next M lines: each line gives a directed edge from u to v.

## Output Format

A single integer — the number of distinct paths from 1 to N.

## Constraints

- `2 <= N <= 100`
- `0 <= M <= N*(N-1)/2`
- The graph is guaranteed to be a DAG.
- Edges only go from lower-numbered to higher-numbered vertices (topological order is 1, 2, ..., N).

## Examples

**Example 1**
```
Input:
4 4
1 2
1 3
2 4
3 4

Output:
2
```
Paths: 1→2→4 and 1→3→4.

**Example 2**
```
Input:
4 5
1 2
1 3
2 3
2 4
3 4

Output:
3
```
Paths: 1→2→4, 1→3→4, 1→2→3→4.

**Example 3**
```
Input:
2 1
1 2

Output:
1
```

## Hint

Use dynamic programming. Let `dp[v]` = number of paths from 1 to v. Process vertices in order 1..N. `dp[1] = 1`. For each edge `(u, v)`, add `dp[u]` to `dp[v]`. Answer is `dp[N]`.
