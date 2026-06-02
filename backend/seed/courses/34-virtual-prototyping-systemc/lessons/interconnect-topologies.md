# Crossbars and NoC Topologies

As SoCs grow to dozens of masters and targets, a single shared bus becomes a bottleneck. Two architectural alternatives — **crossbars** and **Networks-on-Chip (NoCs)** — provide higher throughput by allowing multiple transactions to travel simultaneously.

## Shared Bus vs. Crossbar vs. NoC

| Property | Shared Bus | Crossbar | NoC |
|----------|-----------|----------|-----|
| Concurrent paths | 1 | min(M, T) | Many |
| Scalability | Poor (O(N)) | Moderate (O(M×T)) | Good (O(N log N)) |
| Latency (unloaded) | Low | Low | Higher (hops) |
| Area / complexity | Low | High for large N | Moderate–High |
| Typical use | APB peripherals | AXI high-perf fabric | Many-core chips |

## Crossbar Switch

A crossbar creates a direct connection path between any master and any target, simultaneously. An M×T crossbar can support M independent transactions at the same moment, as long as each goes to a different target.

```
        T0   T1   T2
M0     [X]  [ ]  [ ]   ← M0 is talking to T0
M1     [ ]  [X]  [ ]   ← M1 is talking to T1 (simultaneously)
M2     [ ]  [ ]  [X]   ← M2 is talking to T2 (simultaneously)
```

### TLM Crossbar Model

A TLM crossbar is structurally identical to a bus — it has M target sockets and T initiator sockets — but it allows concurrent `b_transport()` calls to different targets without locking a global mutex:

```cpp
void b_transport(int master_id,
                 tlm::tlm_generic_payload& txn,
                 sc_time& delay) {
    int target_idx = decode(txn.get_address());
    // Lock only the target, not the whole fabric
    target_mutex_[target_idx].lock();
    delay += XBAR_LATENCY;
    target_socket[target_idx]->b_transport(txn, delay);
    target_mutex_[target_idx].unlock();
}
```

Per-target mutexes replace the global mutex, enabling true parallelism.

## Network-on-Chip (NoC)

A NoC replaces point-to-point wires with a packet-switched network. Each master connects to a **router**, and packets travel hop-by-hop to reach their destination router, which connects to the target.

### Common NoC Topologies

| Topology | Description | Latency | Bandwidth |
|----------|-------------|---------|-----------|
| Ring | Nodes in a circle | O(N/2) hops | Limited |
| Mesh (2D) | Grid of routers | O(√N) hops | Good |
| Torus | Mesh with wrap-around | Lower than mesh | Better |
| Fat tree | Tree with wider links at top | O(log N) | Excellent |
| Butterfly | Multi-stage | O(log N) | Excellent |

### TLM NoC Model

A NoC model adds per-hop latency and queuing. The key parameters:

```cpp
struct NocConfig {
    int    hops;            // number of router hops between src and dst
    double link_bw_gbps;    // per-link bandwidth
    double router_delay_ns; // per-hop routing latency
};

sc_time compute_noc_latency(const NocConfig& cfg, uint32_t bytes) {
    double hop_delay_ns = cfg.hops * cfg.router_delay_ns;
    double transfer_ns  = (bytes * 8.0) / (cfg.link_bw_gbps * 1.0);
    return sc_time(hop_delay_ns + transfer_ns, SC_NS);
}
```

## Modeling Contention in Crossbars

Contention occurs when two masters try to reach the **same** target simultaneously. In that case the second master must wait, just as in a shared bus:

- **No contention** (different targets): both proceed in parallel, zero extra latency.
- **Contention** (same target): one waits for the target's mutex. Latency = first transaction's duration.

This is why benchmark results often show near-ideal scaling up to the number of unique targets.

## When to Use Which

- **Shared bus**: ≤4 masters, low bandwidth, simple design (APB ring, debug access ports).
- **Crossbar**: 4–16 masters, high-performance fabric, predictable traffic patterns (AMBA NIC-400 style).
- **NoC**: >16 masters, heterogeneous traffic, tile-based many-core (ARM CMN-700, Intel mesh).

## Common Pitfalls

- **Modeling a crossbar as a shared bus**: Kills simulation accuracy; misses the parallelism that makes crossbars valuable.
- **Ignoring NoC queuing delay**: A NoC under heavy load can saturate links and add significant queuing latency. A fixed-hop model is optimistic.
- **Forgetting arbitration at output ports**: Even a crossbar needs per-output-port arbitration when two masters target the same output.

**Interview answer:** "A crossbar allows simultaneous transactions between different master-target pairs by using per-target locks instead of a global bus mutex. A NoC routes packets over a multi-hop switched network, trading lower per-link area for O(log N) hop latency. The right choice depends on the number of masters, traffic patterns, and area budget."
