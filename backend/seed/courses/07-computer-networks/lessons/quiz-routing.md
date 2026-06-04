# Quiz: Network Routing

**Q1. In distance-vector routing, what does each router share with its neighbors?**
- [ ] Its complete link-state database (full topology)
- [x] Its own routing table (destination, cost, next-hop) — not the full topology
- [ ] Only the link costs to directly connected neighbors
- [ ] The AS-path for every known destination

**Q2. Which algorithm does OSPF use to compute shortest paths after building the full network topology?**
- [ ] Bellman-Ford (iterative relaxation over all edges)
- [ ] Floyd-Warshall (all-pairs shortest paths)
- [x] Dijkstra's shortest-path algorithm (single-source, greedy)
- [ ] A* search (heuristic-guided Dijkstra)

**Q3. What is the "count-to-infinity" problem and which protocol family does it affect?**
- [x] Distance-vector protocols can loop indefinitely when a link fails — routers keep advertising incrementally worse costs to each other. RIP uses a 15-hop limit (16 = infinity) to bound this.
- [ ] Link-state routers disagree on the topology because LSAs are lost, causing routing loops that grow to 255 hops.
- [ ] BGP routers reject routes after the AS-path grows past a configurable maximum, causing unreachability.
- [ ] OSPF miscalculates costs on high-bandwidth links because it uses hop count instead of bandwidth.

**Q4. A router receives a packet destined for 10.10.20.5. Its routing table has these entries: 10.0.0.0/8 (GW1), 10.10.0.0/16 (GW2), 10.10.20.0/24 (GW3), 0.0.0.0/0 (DEFAULT). Which entry wins?**
- [ ] 10.0.0.0/8 via GW1 (first matching entry)
- [ ] 0.0.0.0/0 via DEFAULT (default always matches)
- [ ] 10.10.0.0/16 via GW2 (second most-specific match)
- [x] 10.10.20.0/24 via GW3 (longest prefix match — most specific wins)

**Q5. What distinguishes BGP from OSPF?**
- [ ] BGP uses Dijkstra while OSPF uses Bellman-Ford.
- [ ] BGP operates inside a single Autonomous System; OSPF connects multiple ASes.
- [x] BGP is a path-vector inter-AS protocol that carries AS-path and business-policy attributes; OSPF is an intra-AS link-state protocol optimizing purely for shortest path.
- [ ] BGP is faster to converge because it uses flooding rather than periodic updates.

**Q6. A packet destined for 192.168.1.200 is matched against two routes: 192.168.1.0/24 and 192.168.1.128/25. Which route is selected, and why?**
- [ ] 192.168.1.0/24, because it was added to the routing table first.
- [ ] 192.168.1.0/24, because it covers a larger address range.
- [x] 192.168.1.128/25, because it has a longer prefix length (25 > 24) — longest prefix match always selects the most specific route.
- [ ] The router sends to both interfaces (multipath routing is the default).
