# Exercise: BFS Shortest Path

Use BFS to find shortest distances from a source vertex in an unweighted graph.

## Why BFS Gives Shortest Paths

BFS explores vertices in non-decreasing order of their distance from the source. The first time a vertex is discovered, it is reached via the shortest path — no shorter path can arrive later because all paths of shorter length were already explored.

## Template

```python
from collections import deque
import sys

def solve():
    data = sys.stdin.read().split()
    idx = 0
    V, E = int(data[idx]), int(data[idx+1])
    idx += 2
    graph = [[] for _ in range(V)]
    for _ in range(E):
        u, v = int(data[idx]), int(data[idx+1])
        idx += 2
        graph[u].append(v)
        graph[v].append(u)
    s = int(data[idx])

    dist = [-1] * V
    dist[s] = 0
    q = deque([s])
    while q:
        node = q.popleft()
        for nb in graph[node]:
            if dist[nb] == -1:
                dist[nb] = dist[node] + 1
                q.append(nb)
    for v in range(V):
        print(v, dist[v])

solve()
```
