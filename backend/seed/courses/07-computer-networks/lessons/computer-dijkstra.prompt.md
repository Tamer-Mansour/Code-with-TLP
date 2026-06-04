# Dijkstra Shortest Path for Link State Routing

Simulate Dijkstra's algorithm as used in link-state routing (OSPF).

## Input Format

```
<N> <E>
<u1> <v1> <w1>
...  (E lines)
<S>
```

- Line 1: `N` (number of routers, 1-indexed) and `E` (number of undirected links).
- Next `E` lines: each contains three integers `u v w` — an undirected link between routers `u` and `v` with cost `w`.
- Last line: source router `S`.

## Output Format

Print the shortest distance from `S` to every other node in **ascending order of node ID**, one per line:

```
Node X: D
```

If a node is unreachable from `S`, print `Node X: INF`.

The source node itself is **not printed**.

## Constraints

- 2 ≤ N ≤ 100
- 1 ≤ E ≤ 500
- 1 ≤ w ≤ 1000
- All node IDs are 1-indexed integers in range [1, N]

## Examples

**Input:**
```
5 6
1 2 2
1 3 4
2 3 1
2 4 7
3 5 3
4 5 2
1
```
**Output:**
```
Node 2: 2
Node 3: 3
Node 4: 8
Node 5: 6
```

**Input:**
```
4 3
1 2 5
2 3 3
3 4 2
1
```
**Output:**
```
Node 2: 5
Node 3: 8
Node 4: 10
```

**Input:**
```
4 2
1 2 1
1 3 2
1
```
**Output:**
```
Node 2: 1
Node 3: 2
Node 4: INF
```
