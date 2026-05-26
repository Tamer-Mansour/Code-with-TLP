# What is a Network?

A **computer network** is a collection of interconnected devices that can exchange data. From two laptops sharing files over Wi-Fi to billions of servers handling global Internet traffic, the principles are the same: nodes, links, and protocols. Grasping these fundamentals lets you reason clearly about performance, failure modes, and security in every networked system you build or operate.

## Key Concepts

### Nodes and Links

- **Node** – any device with a network interface: computers, routers, phones, printers, IoT sensors.
- **Link** – a physical or logical channel connecting two or more nodes. Links can be wired (Ethernet, fiber) or wireless (Wi-Fi, cellular).
- **Bandwidth** – the maximum data rate of a link, measured in bits per second (bps). A modern home router typically offers 100 Mbps–1 Gbps over Ethernet.
- **Latency** – the time for one bit to travel from source to destination, also called propagation delay. It is bounded by the speed of light (~200,000 km/s in fiber) and cannot be engineered away.
- **Jitter** – variation in latency from packet to packet. High jitter is particularly harmful for real-time audio and video.

### Network Topologies

Topology describes the physical or logical arrangement of nodes and links:

```
Bus:   A ─────┬─────── B ─────┬─────── C
              │               │
              D               E

Star:             Switch
              /     |     \
            A       B      C

Ring:    A ─── B ─── C ─── D
         └─────────────────┘

Mesh:    A ─── B
         │ × × │
         C ─── D   (every node connects to every other)
```

| Topology | Fault Tolerance | Cable Cost | Scalability | Notes                           |
|----------|-----------------|------------|-------------|----------------------------------|
| Bus      | Low             | Low        | Poor        | Single break kills entire segment|
| Star     | Medium          | Medium     | Good        | Switch failure stops all traffic |
| Ring     | Medium          | Medium     | Medium      | Token Ring (legacy)              |
| Mesh     | High            | High       | Good        | Used in data-center fabrics      |
| Tree     | Medium          | Medium     | Good        | Hierarchical; common in campus   |

Modern LANs almost universally use the **star** topology with an Ethernet switch at the center. Data-center networks use **leaf-spine** (a two-tier mesh) for low latency and high bisection bandwidth.

### Network Scale

| Name | Acronym | Typical Reach | Example |
|------|---------|---------------|---------|
| Personal Area Network | PAN | ~10 m | Bluetooth headset ↔ phone |
| Local Area Network | LAN | Building / Campus | Office Ethernet |
| Metropolitan Area Network | MAN | City | Municipal fiber ring |
| Wide Area Network | WAN | Country / World | MPLS leased lines |
| Internet | — | Global | BGP-connected AS mesh |

The **Internet** is a global WAN — literally a *network of networks* — where thousands of independent Autonomous Systems (ASes) exchange routing information using the Border Gateway Protocol (BGP). Each AS is identified by a globally unique ASN (e.g., AS15169 = Google).

## Switching Techniques

Two fundamental approaches carry data across a network:

### Circuit Switching (traditional telephone system)

A dedicated physical path is reserved for the entire call duration before any data flows. Every intermediate switch allocates a fixed slice of bandwidth (called a *circuit*) for the connection.

- **Pros:** Guaranteed, constant bandwidth; no queuing delay once the circuit is established; predictable for voice.
- **Cons:** Wastes capacity during silences; setup takes time; poor utilization (a 64 Kbps voice circuit carries 0 bits/s during silence, yet the bandwidth is still reserved).

### Packet Switching (the Internet)

Data is divided into **packets** — small chunks, typically up to 1500 bytes of payload — each carrying a header with source and destination addresses. Packets are forwarded independently through the network and reassembled at the destination.

```
Packet format (simplified):
+─────────────────────+─────────────────────+
│       Header        │       Payload       │
│  (src, dst, seq#)   │   (actual data)     │
+─────────────────────+─────────────────────+
```

Routers use **store-and-forward**: they receive the entire packet, check for errors, look up the destination in the routing table, then forward it out the appropriate interface.

- **Pros:** Statistical multiplexing — links are shared efficiently among many users; resilient (packets can take different paths around failures); easy to add new applications.
- **Cons:** Variable delay (queuing in routers); no guaranteed bandwidth; packets can arrive out of order.

### Statistical Multiplexing

Packet switching exploits the fact that users are bursty. A 10 Mbps link shared by 100 users each needing 100 Kbps on average can serve all of them simultaneously, yet would require 10 Mbps × 100 = 1 Gbps capacity under circuit switching.

## Bandwidth vs. Throughput vs. Latency

These three metrics are frequently confused:

- **Bandwidth** is the *capacity* of a link (maximum possible rate). A fiber link may have 10 Gbps of bandwidth.
- **Throughput** is the *actual* data rate achieved end-to-end, which is always ≤ bandwidth. It is limited by the bottleneck link, congestion, and protocol overhead.
- **Latency** is the one-way *delay* for a single packet to travel from source to destination. It has four components:
  1. **Propagation delay** = distance ÷ propagation speed.
  2. **Transmission delay** = packet size ÷ link bandwidth (time to push all bits onto the wire).
  3. **Processing delay** = time for a router to look up the destination in its routing table.
  4. **Queuing delay** = time waiting in a router's output queue.

**Example:** A 1 MB file sent over a 1 Gbps link with 50 ms one-way latency:
- Transmission delay: 8 Mb ÷ 1000 Mbps = 8 ms
- Propagation delay: 50 ms
- Total one-way delay ≈ 58 ms

A high-bandwidth transatlantic cable still has ~70 ms of latency due to the speed of light. You can have high bandwidth but terrible throughput if the network is congested.

## Why Protocols?

Without agreed-upon rules, two devices cannot communicate meaningfully. A **protocol** defines:

1. **Syntax** — the format of messages: which bits go in which fields, byte order (big-endian / little-endian), encoding.
2. **Semantics** — what each field means and what action to take on receipt.
3. **Timing** — who speaks first, how handshakes work, what happens on timeout, and how to handle lost or duplicate messages.

Every layer of the network stack has its own protocol, and they work together through a well-defined contract: each layer provides a service to the layer above and uses the service of the layer below, without knowledge of the internal workings of other layers. This **layering principle** is the reason the Internet can evolve — HTTP/3 replaced the transport without changing IP, and fiber replaced copper without changing TCP.

## Units and Conversions

When reading specifications, keep track of bits vs. bytes:

| Unit  | Abbreviation | Value     |
|-------|-------------|-----------|
| bit   | b           | 1 bit     |
| byte  | B           | 8 bits    |
| Kbps  | —           | 1,000 b/s |
| Mbps  | —           | 10^6 b/s  |
| Gbps  | —           | 10^9 b/s  |
| KB    | —           | 1,024 B   |
| MB    | —           | 1,048,576 B |

Note that network speeds are in **bits per second** (Mbps, Gbps) while file sizes are in **bytes** (MB, GB). A 100 Mbps connection downloads a 100 MB file in 100 MB × 8 b/B ÷ 100 Mbps = 8 seconds.
