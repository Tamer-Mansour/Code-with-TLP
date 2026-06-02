# When Polling Actually Wins

Interrupts are usually taught as the "right" answer for I/O, and in general-purpose operating systems they are. But in high-performance and real-time systems, polling frequently outperforms interrupt-driven I/O. Understanding when and why is a signal of senior-level systems knowledge.

## The Cost of an Interrupt

Handling an interrupt is not free. Each interrupt forces the CPU to:

- Finish the current micro-op and reach a safe instruction boundary.
- Save all general-purpose registers (or at least the caller-saved set).
- Load the ISR's code — which may evict cache lines.
- Execute the ISR logic.
- Restore registers and resume the previous context.

On modern x86 hardware this round-trip costs roughly **1–5 microseconds** in the best case. If a 10 Gbps NIC can deliver a new packet every 67 nanoseconds, firing an interrupt per packet would consume the entire CPU just handling ISRs — leaving zero time to process the packets themselves.

## High-Speed Networking: DPDK and Kernel Bypass

**DPDK** (Data Plane Development Kit) dedicates entire CPU cores to polling network queues in tight loops — no interrupts, no context switches, no scheduler involvement. The result is single-digit microsecond latency and multi-million packets-per-second throughput that interrupt-driven kernels cannot match.

```c
// DPDK polling loop (conceptual)
while (running) {
    nb_rx = rte_eth_rx_burst(port, queue, pkts, MAX_PKT_BURST);
    if (nb_rx > 0) {
        process_packets(pkts, nb_rx);
    }
    // No sleep, no yield — core is dedicated
}
```

The tradeoff: that core is 100% busy even when traffic is zero. For a cloud router handling millions of packets per second, this is a worthwhile exchange.

## NVMe Storage: Completion Polling

Modern NVMe SSDs complete I/O operations in 70–150 µs. The Linux `io_uring` subsystem supports a **polling mode** where the kernel spins on the NVMe completion queue rather than waiting for an interrupt. At high IOPS rates (100K+ ops/sec) this lowers latency by eliminating ISR overhead and can increase throughput significantly.

```bash
# io_uring polling mode — enabled per-queue
# Latency improves at high queue depth when completions arrive rapidly
```

## Spinlocks: Polling Inside the Kernel

Spinlocks are a form of polling: a CPU spins reading a lock variable rather than blocking. They are preferred over sleeping locks when:

- The critical section is very short (a few instructions).
- The holder is running on another CPU and will release soon.
- Sleeping is not allowed (e.g., inside an ISR or with interrupts disabled).

```c
spin_lock(&my_lock);
/* very short critical section */
spin_unlock(&my_lock);
```

If the holder is preempted and the wait is long, spinning wastes the entire quantum — so spinlocks are only correct when hold times are bounded and short.

## Decision Heuristic

| Condition | Prefer |
|---|---|
| Device completes in < ~10 µs | Polling |
| Device completes in > ~100 µs | Interrupts |
| Rate > ~500K events/sec | Polling (interrupt storm risk) |
| Rate < ~10K events/sec | Interrupts |
| Dedicated core available | Polling |
| General-purpose, multi-tenant | Interrupts |

## The "Hybrid" Model: NAPI

Linux's **NAPI** (New API) for network drivers blends both:

1. The first packet triggers an interrupt.
2. The ISR disables further interrupts for that device and schedules a polling function.
3. The polling function drains the receive queue in a budget-limited loop.
4. When the queue is empty (or budget exhausted), interrupts are re-enabled.

This avoids interrupt storms at high traffic while remaining energy-efficient at low traffic.

## Interview Answer

> **Q: When is polling better than interrupts?**
>
> "Polling wins when devices are extremely fast (completion in microseconds), when event rates exceed hundreds of thousands per second (risking interrupt storms), or when a dedicated CPU core is available — as in kernel-bypass networking (DPDK) or NVMe polling mode. The key insight is that interrupt overhead is fixed, so at high enough rates it dominates."
