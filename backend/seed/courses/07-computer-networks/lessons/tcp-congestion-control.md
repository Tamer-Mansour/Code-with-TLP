# TCP Congestion Control

TCP congestion control is a distributed algorithm that runs simultaneously on millions of senders without any central coordinator, yet keeps the Internet from collapsing under its own load. This lesson goes deep into how it works, why it was designed this way, and how modern variants like BBR improve on the classic AIMD approach.

## Why Congestion Control Is Necessary

A network without congestion control would experience **congestion collapse**: as load approaches capacity, routers' queues overflow and begin dropping packets. Senders retransmit, adding more traffic. Throughput spirals to near zero even though the links are saturated — a state observed on the early ARPANET in 1986 before Van Jacobson introduced TCP congestion control.

TCP's congestion control is **cooperative and implicit**:
- Cooperative: every TCP sender voluntarily backs off when congestion is detected.
- Implicit: congestion is inferred from observable events (packet loss, delay) rather than explicit signals from routers.

Without loss-based congestion control, UDP flows can freely occupy all available bandwidth. This is why QUIC (HTTP/3) implements its own congestion control on top of UDP.

## The Congestion Window (cwnd)

TCP limits the amount of unacknowledged data in flight using the **congestion window**:

```
Bytes in flight ≤ min(cwnd, rwnd)
```

Where `rwnd` is the receiver's advertised window (flow control). Congestion control adjusts `cwnd` based on network conditions. The effective sending rate is approximately:

```
rate ≈ cwnd / RTT   (bytes per second)
```

If RTT = 100 ms and cwnd = 64 KB:
`rate ≈ 65,536 bytes / 0.1 s ≈ 524 Kbps`

## Phase 1: Slow Start

**Goal:** quickly find the network's available bandwidth from a cold start.

- Initial: `cwnd = IW` (initial window; typically 10 MSS since RFC 6928).
- For each ACK received: `cwnd += MSS` → effectively **cwnd doubles each RTT** (exponential growth).
- Slow start runs until: (a) `cwnd ≥ ssthresh`, (b) a loss event occurs, or (c) the sender runs out of data.

```
RTT 1: cwnd=10, send 10 segments, receive 10 ACKs → cwnd=20
RTT 2: cwnd=20, send 20 segments, receive 20 ACKs → cwnd=40
RTT 3: cwnd=40 (if ssthresh=32, we crossed → switch to CA)
```

"Slow" refers to starting with a small window (not flooding the network immediately), not to the rate of growth.

## Phase 2: Congestion Avoidance (AIMD)

**Goal:** probe for more bandwidth cautiously once `cwnd ≥ ssthresh`.

**Additive Increase (AI):** for each RTT during which no loss occurs:
```
cwnd += MSS × (MSS / cwnd)    # per ACK — roughly +1 MSS per RTT
```

Linear growth — 1 MSS added per round-trip time. This probes gently so that when congestion is detected, not too much has been wasted.

**Multiplicative Decrease (MD):** when loss is detected:
- **Three duplicate ACKs (fast retransmit path):**
  ```
  ssthresh = cwnd / 2
  cwnd = ssthresh          # TCP Reno: halve and stay in CA
  ```
- **Timeout (more severe — link may be broken):**
  ```
  ssthresh = cwnd / 2
  cwnd = 1 MSS             # restart slow start from scratch
  ```

The AIMD "sawtooth" pattern:

```
cwnd (MSS)
│   slow start             CA            loss  CA
│  /                    .─────.         .──────
│ /               .──────      ╲     .───
│/         .──────               ╲.───
└────────────────────────────────────────────── time (RTTs)
  IW     ss  ca  ss    ca    loss  ss  ca
```

## Fast Retransmit and Fast Recovery

Three duplicate ACKs mean the receiver has received later segments but is still waiting for one specific lost segment. The network is not completely broken — just one segment was lost.

**Fast retransmit:** retransmit the missing segment immediately without waiting for RTO.

**Fast recovery (TCP Reno):** after fast retransmit, instead of restarting slow start, continue in congestion avoidance at the new (halved) ssthresh. This recovers faster from isolated losses.

**TCP New Reno** improves fast recovery when multiple segments from the same window are lost — it retransmits one lost segment per RTT until all losses in the window are recovered.

## Selective Acknowledgements (SACK)

Standard cumulative ACKs can only recover one loss per RTT (the sender retransmits the lowest unACKed segment). **SACK** (RFC 2018, enabled by default on all modern OS) lets the receiver explicitly inform the sender of which ranges it has received:

```
ACK=1001, SACK: {1501–2001, 2501–3001}
→ Sender knows segment 1001–1500 and 2001–2500 are missing
→ Retransmits both immediately (SACK-based retransmission)
```

SACK dramatically improves recovery when multiple packets are lost in a single window, reducing the number of recovery RTTs.

## Modern Congestion Control Algorithms

### TCP Cubic (RFC 8312 — Linux default since kernel 2.6.19)

AIMD's linear increase is too conservative for high-bandwidth, high-latency paths (e.g., a 10 Gbps link with 100 ms RTT — the BDP is 125 MB; AIMD would take thousands of RTTs to fill the pipe after a loss).

Cubic uses a **cubic function** of time elapsed since the last loss event:

```
cwnd(t) = C × (t − K)³ + W_max

where K = (W_max × β / C)^(1/3)
and β = 0.7 (Cubic's decrease factor vs Reno's 0.5)
```

This produces:
- Aggressive growth when far from the last loss point.
- Slow, cautious growth near W_max (where congestion likely lies).
- Faster recovery after loss (β=0.7 vs 0.5).

### TCP BBR (Bottleneck Bandwidth and Round-trip propagation — Google, 2016)

**Core insight:** traditional loss-based algorithms are reactive. They wait for queues to overflow (causing bufferbloat) and only then back off. BBR directly models the network bottleneck.

BBR estimates two quantities:
- **BtlBW** (bottleneck bandwidth): maximum delivery rate observed over recent RTTs.
- **RTprop** (round-trip propagation time): minimum RTT observed, representing the path's propagation delay with empty queues.

BBR sets:
```
cwnd = 2 × BtlBW × RTprop   (approximately two BDPs)
pacing rate = BtlBW
```

It periodically probes for higher BtlBW (briefly sends at 125% of estimated rate) and lower RTprop (briefly drains the queue by sending at 75% of rate).

**BBR advantages:**
- Keeps queues nearly empty → low latency for interactive flows.
- Throughput 2–100× better than Cubic on paths with high BDP or shallow buffers (cellular, satellite).
- Less sensitivity to random packet loss (wireless links).

**BBR caveats:**
- Less fair to Cubic flows in some scenarios (ongoing research area).
- Slightly more complex to tune.

### Comparison

| Algorithm | Loss signal | Convergence | Best for |
|-----------|-------------|-------------|---------|
| Reno | Packet loss | Slow on high-BDP | Legacy; simple reference |
| Cubic | Packet loss | Faster | Most Internet paths |
| BBR v1 | BW + delay | Fast | High-BDP, wireless, CDNs |
| BBR v2 | BW + delay + loss | Improved fairness | Internet-wide deployment |
| QUIC Cubic | Packet loss | Same as TCP Cubic | HTTP/3 default |

## Explicit Congestion Notification (ECN)

Rather than waiting for packet loss, **ECN** (RFC 3168) allows routers to signal incipient congestion by marking packets (setting the CE bit in the IP header) before their queues overflow. TCP endpoints negotiate ECN during the handshake. On receiving an ECN-marked packet, the receiver echoes it back (ECE flag) and the sender backs off as if a loss had occurred — but without actually losing the packet.

ECN benefits: avoids the latency spike and throughput drop of packet loss. Supported by Linux, Windows, macOS, and most modern switches. Requires both endpoints and intermediate routers to support it.

## Practical Implications for Engineers

- **Download speed ≈ min(cwnd, rwnd) / RTT**: reduce RTT (move servers geographically closer; use CDNs) to improve throughput even without changing bandwidth.
- **Slow-start on new connections**: the first few RTTs of a new TCP connection are slow. HTTP/2 and HTTP/3 reuse connections to amortize this cost.
- **Bufferbloat**: oversized router buffers delay congestion signaling, causing hundreds of milliseconds of queuing latency. Solutions: CoDel, FQ-CoDel, ECN.
- **BBR for backend services**: Google uses BBR on YouTube and Google Search CDN, reporting significant improvement in rebuffering rate and latency.
