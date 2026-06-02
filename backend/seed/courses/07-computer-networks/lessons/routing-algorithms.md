# Routing Algorithms

Every router must answer one question: *given this destination IP address, which interface should I send the packet out of?* The answer comes from a **routing table** built by routing algorithms. There are two fundamental families: **link-state** (each router knows the full topology) and **distance-vector** (each router knows only its neighbors' costs).

## Distance-Vector Routing (Bellman-Ford)

In distance-vector routing, each router maintains a table of *(destination, cost, next-hop)* triples. Routers periodically broadcast their entire table to directly connected neighbors. Each router updates its own table using the **Bellman-Ford equation**:

```
D(x, y) = min over all neighbors v of { cost(x, v) + D(v, y) }
```

Where `D(x, y)` is router x's current best-known cost to reach y.

**Example network:**

```
A ──1── B ──2── C
└──4── D ──1── C
```

Router A's initial distance-vector (it only knows its own link costs):

| Destination | Cost | Next-hop |
|-------------|------|----------|
| A           | 0    | —        |
| B           | 1    | B        |
| D           | 4    | D        |
| C           | ∞    | —        |

After receiving B's table (B→C cost=2), A updates: `D(A,C) = cost(A,B) + D(B,C) = 1 + 2 = 3` via B. After receiving D's table (D→C cost=1), A recomputes: `D(A,C) via D = 4 + 1 = 5`. The best path remains A→B→C at cost 3.

**Count-to-Infinity Problem:** When a link fails, distance-vector routers can loop indefinitely, each advertising a slightly worse cost. RIP uses a **maximum hop count of 15** (infinity = 16) and **split horizon** (don't advertise a route back to the neighbor you learned it from) to mitigate this.

Real-world protocol using distance-vector: **RIP (Routing Information Protocol)**.

## Link-State Routing (Dijkstra's Algorithm)

In link-state routing, each router floods the entire network with **Link-State Advertisements (LSAs)** containing its directly connected links and their costs. Every router builds an identical graph of the full network, then runs **Dijkstra's shortest-path algorithm** independently.

```python
import heapq

def dijkstra(graph, source):
    # graph: {node: [(cost, neighbor), ...]}
    dist = {node: float('inf') for node in graph}
    dist[source] = 0
    pq = [(0, source)]
    prev = {}

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for cost, v in graph[u]:
            nd = dist[u] + cost
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, prev

graph = {
    'A': [(1, 'B'), (4, 'D')],
    'B': [(1, 'A'), (2, 'C')],
    'C': [(2, 'B'), (1, 'D')],
    'D': [(4, 'A'), (1, 'C')],
}
dist, prev = dijkstra(graph, 'A')
# dist = {'A': 0, 'B': 1, 'C': 3, 'D': 4}
```

Dijkstra runs in O((V + E) log V) with a binary heap. Because every router has the same graph, all routers compute the same shortest-path tree — there are no routing loops.

Real-world protocol using link-state: **OSPF (Open Shortest Path First)**, the dominant intra-domain protocol in enterprise and ISP networks.

## Comparison

| Property             | Distance-Vector (RIP)      | Link-State (OSPF)            |
|----------------------|----------------------------|------------------------------|
| Information shared   | Routing table to neighbors | Full topology via flooding   |
| Algorithm            | Bellman-Ford               | Dijkstra                     |
| Convergence speed    | Slow (may loop)            | Fast                         |
| Scalability          | Poor (15-hop limit for RIP)| Good (area hierarchy in OSPF)|
| Complexity           | Simple to implement        | More complex                 |
| Loop risk            | Yes (count-to-infinity)    | No (complete topology view)  |

## BGP: Inter-AS Routing

Neither RIP nor OSPF is used between Autonomous Systems (ASes) on the public Internet. That role belongs to **BGP (Border Gateway Protocol)**, a **path-vector** protocol. BGP routers exchange full AS-path information so routing loops are detected (a router rejects a path that includes its own AS number). BGP decisions incorporate not just shortest path but also **business policy** — an ISP may prefer routes through a paid transit provider over a cheaper but slower path.

## Longest Prefix Match

Routers select the routing table entry whose network prefix is the *longest* (most specific) match for the destination IP. This is why a packet destined for 10.0.1.45 hits a `/24` route before a `/8` or default (`/0`) route:

```
Route Table:
  10.0.1.0/24   → eth0   (matches, prefix length 24)
  10.0.0.0/8    → eth1   (matches, prefix length 8)
  0.0.0.0/0     → eth2   (default, matches everything)

Destination: 10.0.1.45
Best match: 10.0.1.0/24 → eth0   (longest prefix wins)
```

The exercise in this module challenges you to implement this exact algorithm in Python.
