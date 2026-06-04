# Exercise: Dijkstra Shortest Path for Link State Routing

Link-state routing protocols like **OSPF** work by having every router run Dijkstra's shortest-path algorithm on a shared view of the entire network topology. This exercise asks you to implement that algorithm given a router network described as a weighted undirected graph.

## Background

In OSPF:
1. Every router floods **Link-State Advertisements (LSAs)** describing its directly connected links and their costs.
2. All routers accumulate LSAs to build an identical graph of the full network.
3. Each router independently runs Dijkstra from itself as the source.
4. The resulting shortest-path tree determines the routing table: each destination maps to a next-hop interface.

Your task is step 3: given the graph and a source router, compute the shortest distance to every other node.

## What You Need to Implement

Read a weighted undirected graph from stdin. Run Dijkstra's algorithm from the given source node. Print the shortest distance to every other node in ascending node-ID order.

For the full input/output format and constraints, see the exercise prompt.

## Algorithm Skeleton

```python
import heapq

def dijkstra(graph, n, src):
    dist = [float('inf')] * (n + 1)   # 1-indexed
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                   # stale entry — skip
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))
    return dist
```

The priority queue (min-heap) ensures the node with the smallest tentative distance is always relaxed next — this is the key invariant of Dijkstra's algorithm.

## Complexity

- **Time:** O((V + E) log V) with a binary heap.
- **Space:** O(V + E) for the adjacency list and distance array.

## Further Reading

- *An Introduction to Computer Networks* by Peter Lars Dordal — Chapter 13, Routing:
  https://eng.libretexts.org/Bookshelves/Computer_Science/Networks/An_Introduction_to_Computer_Networks_(Dordal)
- *Computer Networks (MIT OCW 6.829)* by Hari Balakrishnan — Lecture notes on link-state routing:
  https://ocw.mit.edu/courses/6-829-computer-networks-fall-2002/
