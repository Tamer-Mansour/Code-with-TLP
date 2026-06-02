# Video: Routing Algorithms and Protocols

This video covers how routers decide where to forward packets: distance-vector routing (Bellman-Ford), link-state routing (Dijkstra's algorithm), and real-world protocols including RIP, OSPF, and BGP. It explains intra-AS vs. inter-AS routing and the role of BGP in connecting the Internet's autonomous systems.

Key takeaways: link-state routing (OSPF) gives each router a full map and computes shortest paths independently; distance-vector routing (RIP) shares route tables with neighbors and can suffer from the count-to-infinity problem; BGP is a path-vector protocol used between ISPs that incorporates business policy, not just shortest paths. Animated diagrams show Dijkstra's algorithm running step by step.

Timestamps: 0:00 — routing fundamentals; ~15 min — Bellman-Ford / distance-vector; ~35 min — Dijkstra / link-state; ~55 min — OSPF deep dive; ~1:15 — BGP and inter-AS routing; ~1:35 — longest prefix match implementation.
