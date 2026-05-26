# Routing and NAT

IP packets travel from source to destination through a series of **routers**. Each router must decide which outgoing interface to forward a packet on — a decision called **packet forwarding**, driven by a **routing table** built by **routing protocols**. **NAT (Network Address Translation)** lets many private-address devices share a single public IP, a workaround that has become indispensable given IPv4 exhaustion.

## How Routers Work

A router connects two or more IP networks. It operates at **Layer 3** (the IP layer) and processes each packet independently. For every incoming packet, a router:

1. Receives the entire Ethernet frame on an interface, strips the Ethernet header.
2. Reads the IP destination address.
3. Looks up the destination in its **routing table** using longest-prefix match.
4. Decrements the IP **TTL** field by 1. If TTL reaches 0, discards the packet and sends an ICMP Time Exceeded back to the source.
5. Rewrites the Ethernet frame with the next-hop MAC address and the router's own MAC as source.
6. Transmits the frame out the chosen interface.

```
Router R1 — routing table:
Destination/Prefix    Next Hop         Interface   Metric
10.0.1.0/24           directly conn.   eth0        0
10.0.2.0/24           directly conn.   eth1        0
172.16.0.0/16         10.0.1.254       eth0        1
0.0.0.0/0             203.0.113.1      eth2        10   ← default route
```

### Longest Prefix Match — Worked Example

Routing table lookup for destination `10.0.1.45`:

| Entry | Prefix | Match? | Prefix length |
|-------|--------|--------|---------------|
| A | 10.0.1.0/24 | Yes | 24 bits |
| B | 10.0.0.0/8 | Yes | 8 bits |
| C | 0.0.0.0/0 | Yes | 0 bits |

**Longest match wins: entry A (/24).** The router forwards out eth0. The `0.0.0.0/0` default route is the catch-all — any packet with no more specific match goes there.

This algorithm is implemented in hardware using **TCAM (Ternary Content Addressable Memory)** in high-speed routers, enabling lookups at line rate (terabits per second).

## Routing Protocols

Routers learn routes in three ways: **directly connected** networks (always present), **static routes** (manually configured), and **dynamic routes** (learned via routing protocols).

### Distance-Vector Protocols

Each router periodically broadcasts its routing table to neighbors. Neighbors incorporate the received information, adding their own hop cost. Routes propagate hop by hop.

**RIP (Routing Information Protocol)** — RFC 2453
- Metric: hop count (max 15 hops — anything beyond is "unreachable").
- Updates every 30 seconds.
- Simple; suitable for very small networks.
- Weakness: slow convergence (count-to-infinity problem); 15-hop limit.

### Link-State Protocols

Each router floods a **Link-State Advertisement (LSA)** describing its links and their costs to *all* routers in the area. Every router builds a complete topology map and runs **Dijkstra's shortest-path algorithm** to compute routes.

**OSPF (Open Shortest Path First)** — RFC 2328
- Metric: *cost* = reference bandwidth / interface bandwidth (e.g., cost 1 for GigE, cost 10 for FastEthernet by default).
- Fast convergence: LSA flooding propagates in seconds.
- Scales through hierarchical **areas** (all routers in Area 0 = backbone; other areas connect to it).
- Authentication supported.
- Most common IGP in enterprise and ISP networks.

**IS-IS** — similar to OSPF; preferred by many large ISP backbone networks.

### Comparison: Interior Gateway Protocols

| Protocol | Type | Metric | Convergence | Scale | Notes |
|----------|------|--------|-------------|-------|-------|
| RIP | Distance-vector | Hop count | Slow (30 s) | Tiny | Legacy |
| OSPF | Link-state | Cost (bandwidth) | Fast (seconds) | Large | Enterprise standard |
| EIGRP | Hybrid (Cisco) | Composite (BW+delay) | Fast | Medium | Cisco proprietary |
| IS-IS | Link-state | Metric (configurable) | Fast | Very large | ISP backbones |

### BGP: The Internet's Routing Protocol

**BGP (Border Gateway Protocol)** — RFC 4271 — is the **Exterior Gateway Protocol (EGP)** used between Autonomous Systems. BGP is a **path-vector** protocol: it advertises not just reachability but the full AS path to a prefix.

```
AS65001 ── BGP peering ── AS3356 (Level3) ── BGP ── AS15169 (Google)
```

BGP route selection considers (in order of priority):
1. Highest **local preference** (set by policy).
2. Shortest **AS_PATH** (fewest AS hops).
3. Lowest **MED** (Multi-Exit Discriminator — hints from neighbor).
4. eBGP over iBGP routes.
5. Lowest IGP cost to the BGP next-hop.
6. Tie-breaking (router ID).

BGP is deliberately policy-driven rather than metric-driven. An ISP can prefer a more expensive route for business reasons (peering agreements, traffic engineering).

**BGP hijacking** is a serious security issue: a rogue AS can advertise a more specific prefix for address space it doesn't own, attracting traffic meant for someone else. Mitigated by RPKI (Resource Public Key Infrastructure) and route filtering.

## ICMP: Internet Control Message Protocol

ICMP (RFC 792) is a Layer-3 signaling protocol carried inside IP packets. It is not a transport protocol — it doesn't carry application data.

Common ICMP message types:

| Type | Code | Name | Used by |
|------|------|------|---------|
| 0 | 0 | Echo Reply | ping |
| 3 | — | Destination Unreachable | port/host unreachable |
| 8 | 0 | Echo Request | ping |
| 11 | 0 | Time Exceeded | traceroute (TTL=0 in transit) |
| 11 | 1 | Fragment Reassembly Timeout | IP fragmentation |

`ping` and `traceroute` both rely on ICMP:
- **ping**: sends ICMP Echo Request; target replies with Echo Reply.
- **traceroute**: sends packets with TTL=1, 2, 3, … Each router that decrements TTL to 0 sends ICMP Time Exceeded, revealing the path.

## NAT: Network Address Translation

IPv4 has ~4.3 billion addresses — far fewer than the devices on Earth. **NAT** (RFC 3022) lets an entire home or office network share a single public IP by rewriting IP and port numbers at the gateway.

### How NAT Works — Full Walkthrough

```
Private Network                   NAT Router                  Internet
192.168.1.100:54321  ──────────►  203.0.113.5:40001  ──────► 93.184.216.34:443
192.168.1.101:54322  ──────────►  203.0.113.5:40002  ──────► 93.184.216.34:443
192.168.1.100:54323  ──────────►  203.0.113.5:40003  ──────► 8.8.8.8:53
```

The NAT router's **translation table**:

| Private IP:Port        | Public IP:Port          | Remote IP:Port          | Protocol |
|------------------------|-------------------------|-------------------------|---------|
| 192.168.1.100:54321    | 203.0.113.5:40001       | 93.184.216.34:443       | TCP      |
| 192.168.1.101:54322    | 203.0.113.5:40002       | 93.184.216.34:443       | TCP      |
| 192.168.1.100:54323    | 203.0.113.5:40003       | 8.8.8.8:53              | UDP      |

**Outgoing:** rewrite `(src_ip=192.168.1.100, src_port=54321)` → `(src_ip=203.0.113.5, src_port=40001)`.

**Incoming:** packet arrives at `203.0.113.5:40001` → look up table → rewrite to `192.168.1.100:54321` → forward to private network.

This is **NAPT** (Network Address and Port Translation), also called PAT or IP masquerading. The public IP is shared across all translations; the port number distinguishes them.

### NAT Types (relevant for P2P and WebRTC)

| Type | Behavior | P2P traversal |
|------|----------|--------------|
| Full-cone (one-to-one) | Any external host can reach the mapped port | Easiest |
| Address-restricted cone | Only hosts the private host has contacted | Possible |
| Port-restricted cone | Must match both remote IP and remote port | Harder |
| Symmetric | Different public port for each remote endpoint | Very hard; requires TURN relay |

**NAT breaks the end-to-end principle**: external hosts cannot initiate connections to devices behind NAT. Solutions:
- **UPnP/NAT-PMP**: router exposes a protocol for internal devices to open ports automatically.
- **STUN** (Session Traversal Utilities for NAT): helps a client discover its public IP:port and attempt direct peer-to-peer communication.
- **TURN** (Traversal Using Relays around NAT): relay server for symmetric NAT where direct traversal fails.
- **IPv6**: eliminates NAT entirely — every device gets a globally routable address.
