# TCP Reliability: How It Works

TCP's guarantee of **reliable, ordered, byte-stream delivery** over an unreliable IP network is one of the greatest achievements in networking engineering. IP is strictly best-effort: it can lose, reorder, duplicate, or corrupt packets. TCP recovers from all of these using only mechanisms at the communicating endpoints — no special network hardware required.

## Sequence Numbers and Acknowledgements

TCP thinks of data as a **byte stream**, not as discrete messages. Every byte has a **sequence number**. The receiver uses **cumulative acknowledgements** (ACKs): the ACK number says "I have received all bytes up to but not including this number — send me the next one."

```
Sender                                  Receiver
  │── Seg(seq=1000, len=500) ─────────► │   (bytes 1000–1499)
  │── Seg(seq=1500, len=500) ─────────► │   (bytes 1500–1999)
  │◄── ACK(ack=2000) ──────────────────  │   "I have 1000–1999, send 2000"
  │── Seg(seq=2000, len=500) ─────────► │
  │◄── ACK(ack=2500) ──────────────────  │
```

Segments can be lost and arrive out of order. TCP handles this cleanly:

```
Sender                                  Receiver
  │── Seg(seq=1000) ──────────────────► │  ACK 1500
  │── Seg(seq=1500) ── LOST ──          │
  │── Seg(seq=2000) ──────────────────► │  ACK 1500 (dup — missing 1500–1999)
  │── Seg(seq=2500) ──────────────────► │  ACK 1500 (dup)
  │── Seg(seq=3000) ──────────────────► │  ACK 1500 (dup)
  │── Retransmit(seq=1500) ───────────► │  ACK 3500 (caught up!)
```

The receiver buffers the out-of-order segments (seq=2000, 2500, 3000) and delivers them all to the application once the gap (seq=1500) is filled.

## Retransmission Mechanisms

TCP has two triggers for retransmission:

### 1. Retransmission Timeout (RTO)

If no ACK is received within the **RTO**, the segment is presumed lost and retransmitted.

**RTO calculation (RFC 6298):**
- Measure the round-trip time for each ACK: `SampleRTT`.
- Compute a smoothed estimate: `SRTT = 0.875 × SRTT + 0.125 × SampleRTT`.
- Compute variance: `DevRTT = 0.75 × DevRTT + 0.25 × |SampleRTT − SRTT|`.
- RTO = SRTT + 4 × DevRTT (minimum 1 second per RFC).

When a timeout occurs, TCP **doubles the RTO** (exponential backoff) to avoid hammering a congested network. This is called **Karn's algorithm** — RTO measurements are suspended during retransmission to avoid contaminating the RTT estimate.

### 2. Fast Retransmit

Three duplicate ACKs (the same ack number repeated) indicate a gap: the receiver has received segments after the gap but is still waiting for the lost one. The sender retransmits immediately **without waiting for the RTO**.

```
Sender                        Receiver
  │── Seg(seq=1) ────────────► │  ACK 2
  │── Seg(seq=2) ── LOST ──    │
  │── Seg(seq=3) ────────────► │  ACK 2 (dup 1 — I have 3, need 2)
  │── Seg(seq=4) ────────────► │  ACK 2 (dup 2)
  │── Seg(seq=5) ────────────► │  ACK 2 (dup 3 — fast retransmit trigger)
  │── Retransmit(seq=2) ──────►│  ACK 6
```

Fast retransmit is typically 3× faster than waiting for RTO.

## Flow Control: Protecting the Receiver

The receiver may be slower than the sender (limited CPU, application reading slowly, full buffers). TCP's **sliding window** prevents the sender from overwhelming the receiver.

The receiver advertises its available buffer space — the **receive window** (`rwnd`) — in every ACK:

```
Sender transmit window = min(cwnd, rwnd)
```

If `rwnd` drops to 0, the sender pauses and sends **1-byte probe segments** periodically to detect when the receiver's buffer frees up (window update from receiver).

**Example:**
- Receiver has a 64 KB buffer.
- Application is reading slowly and has only consumed 20 KB.
- `rwnd = 64 KB − (64 KB − 20 KB) = 20 KB` (available space advertised to sender).
- Sender may not have more than 20 KB of unacknowledged data in flight.

## Congestion Control: Protecting the Network

The *network* itself can be overwhelmed. TCP infers congestion from events (packet loss or delay) and dynamically reduces its sending rate — the **congestion window** (`cwnd`).

```
Effective window = min(cwnd, rwnd)
```

### Phase 1: Slow Start

- Start: `cwnd = 1 MSS` (Maximum Segment Size, typically 1460 bytes on Ethernet).
- After each ACK: `cwnd += 1 MSS` → effectively **doubles cwnd every RTT**.
- This is *exponential* growth, despite the name "slow start" (it's slow compared to sending everything at once, but grows fast).
- Slow start runs until `cwnd ≥ ssthresh` (slow-start threshold) or a loss event.

### Phase 2: Congestion Avoidance (AIMD)

Once `cwnd ≥ ssthresh`:
- **Additive Increase (AI)**: after each full window ACK, `cwnd += 1 MSS`. Linear growth.
- **Multiplicative Decrease (MD)**: on a loss event, `ssthresh = cwnd / 2`, then reduce `cwnd`.

**On three duplicate ACKs (fast retransmit):**
`ssthresh = cwnd / 2`, `cwnd = ssthresh` (TCP Reno). Stay in congestion avoidance (don't go back to slow start).

**On timeout (more severe):**
`ssthresh = cwnd / 2`, `cwnd = 1 MSS` (restart slow start). This is more aggressive because a timeout suggests the network is more severely congested.

```
cwnd (MSS)
   │    Slow start          Cong. Avoid
   │  /                    /      Loss (3 dup ACKs)
   │ /  ssthresh → ───────/          \ ────────────
   │/                                  \  ← new ssthresh = cwnd/2
   └──────────────────────────────────────── time
```

### Modern Congestion Control Algorithms

| Algorithm | Loss signal        | Key characteristic |
|-----------|--------------------|--------------------|
| **TCP Reno** | Packet loss (3 dup ACK or timeout) | Classic; reference implementation |
| **TCP Cubic** | Packet loss | Default in Linux ≥ 2.6.19; faster recovery, cubic growth function |
| **TCP BBR** (Google, 2016) | Bandwidth-delay product estimation | Probes for actual bottleneck bandwidth; much better on high-BDP paths (e.g., satellite, transcontinental) |
| **QUIC Cubic/BBR** | Same signals as TCP but per-stream | Used by HTTP/3 |

**BBR (Bottleneck Bandwidth and Round-trip propagation)** deserves special mention: rather than reacting to packet loss, it models the network's bottleneck bandwidth and minimum RTT. It fills the pipe more efficiently without inducing excessive queue latency, which improves throughput by 2–25× on long fat networks.

## Selective Acknowledgements (SACK)

Standard TCP ACKs are cumulative: "I have everything up to byte N." If multiple segments are lost, standard TCP can only infer one loss at a time. **SACK** (RFC 2018) allows the receiver to report which blocks of bytes it has received:

```
ACK=1500, SACK: [2000–2500, 3000–3500]
```

The sender knows exactly which segments to retransmit, avoiding unnecessary retransmissions. SACK is supported by essentially all modern operating systems and enabled by default.

## Connection Teardown and TIME_WAIT

TCP teardown is a **four-way handshake** because each half of the full-duplex connection closes independently:

```
Client [FIN_WAIT_1]  ──── FIN ────────────────────► Server [CLOSE_WAIT]
Client [FIN_WAIT_2]  ◄─── ACK ──────────────────── Server
                     ◄─── FIN ──────────────────── Server [LAST_ACK]
Client [TIME_WAIT]   ──── ACK ────────────────────► Server [CLOSED]
Client waits 2 × MSL (Maximum Segment Lifetime ≈ 60 s) before [CLOSED]
```

**Why TIME_WAIT?** Two reasons:
1. Ensure the final ACK reaches the server. If it is lost, the server retransmits FIN and the client is still there to ACK it.
2. Let any stale packets from the old connection die before the 4-tuple is reused for a new connection.

High-throughput servers (handling tens of thousands of connections/second) can accumulate many TIME_WAIT sockets. Tunable with `tcp_tw_reuse` on Linux, `SO_REUSEADDR`, and the `SO_REUSEPORT` socket option.

## Summary: TCP's Four-Level Reliability Stack

1. **Checksum** — detect corruption per segment.
2. **Sequence numbers + ACKs + retransmission** — recover lost or reordered segments.
3. **Flow control (rwnd)** — protect the receiver from being overrun.
4. **Congestion control (cwnd + AIMD)** — protect the network from collapse.

These mechanisms work together to make TCP robust enough to carry HTTP, SSH, database queries, and file transfers reliably, regardless of what the underlying IP network throws at them.
