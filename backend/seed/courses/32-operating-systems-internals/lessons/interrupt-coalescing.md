# Interrupt Coalescing and Throughput

A device that generates one interrupt per completed operation is simple to program but disastrous at scale. A 10 Gbps NIC receiving minimum-size (64-byte) Ethernet frames generates nearly **15 million packets per second** — and one interrupt per packet would consume entire CPU cores just servicing ISRs. **Interrupt coalescing** solves this by batching multiple completions into a single interrupt.

## The Problem: Interrupt Storms

At high I/O rates, per-operation interrupts create a feedback loop:

1. Device completes operation → fires interrupt.
2. CPU stops, saves context, runs ISR, restores context.
3. By the time the ISR finishes, 10 more operations have completed → 10 more interrupts queued.
4. CPU spends 100% of its time in ISRs, zero time processing data.

This is called an **interrupt storm** or **livelock**. The system appears to receive data (ISRs run) but application throughput is zero.

## Interrupt Coalescing: Wait, Then Interrupt

Coalescing delays the interrupt until one of two conditions is met:

- **Count threshold:** N operations have completed (e.g., 16 packets received).
- **Time threshold:** T microseconds have passed since the first pending completion (e.g., 50 µs).

Whichever fires first triggers a single interrupt. The ISR then processes all pending completions in one pass.

```
Without coalescing (16 packets):   16 ISR entries, 16 context saves
With coalescing (16 packets):      1 ISR entry,   1 context save
                                   ISR loops over 16 completions
```

## Configuring Coalescing in Linux

The `ethtool` command exposes per-NIC coalescing parameters:

```bash
# View current coalescing settings
ethtool -c eth0

# Set: interrupt after 64 RX packets OR 50 µs, whichever comes first
ethtool -C eth0 rx-frames 64 rx-usecs 50

# View interrupt statistics (to verify reduction)
ethtool -S eth0 | grep -i interrupt
```

Typical tuning values for server NICs:

| Workload | rx-usecs | rx-frames |
|---|---|---|
| Low-latency (HFT, gaming) | 0–10 µs | 1 |
| Balanced (web servers) | 50–100 µs | 8–64 |
| Maximum throughput | 200–500 µs | 128–256 |

## The Latency-Throughput Tradeoff

Coalescing is explicitly a tradeoff:

- **More coalescing** → fewer interrupts → higher throughput → higher latency (data waits in the NIC buffer for the coalescing timer to expire).
- **Less coalescing** → more interrupts → lower latency → lower throughput (CPU overhead dominates).

```
Throughput
    ^
    |          ___________
    |         /
    |        /
    |       /
    |______/
    +-----------------------------> Coalescing (rx-usecs)
    Low           High

Latency
    ^
    |____
    |    \
    |     \
    |      \_________________
    +-----------------------------> Coalescing (rx-usecs)
    Low           High
```

## Adaptive Interrupt Moderation (AIM / ITR)

Many modern NICs implement **adaptive** coalescing: the driver or hardware monitors the current interrupt rate and automatically adjusts thresholds.

- Low traffic → reduce coalescing → lower latency.
- High traffic → increase coalescing → higher throughput.

Intel's 82599 NIC calls this **ITR (Interrupt Throttle Rate)**. The driver measures the time between interrupts and tunes the ITR register:

```c
// Intel ixgbe driver (simplified)
void ixgbe_update_itr(struct ixgbe_q_vector *q_vector)
{
    if (packets_per_int > HIGH_THRESHOLD)
        new_itr = IXGBE_MAX_ITR;   // more coalescing
    else if (packets_per_int < LOW_THRESHOLD)
        new_itr = IXGBE_MIN_ITR;   // less coalescing
    ixgbe_write_itr(q_vector, new_itr);
}
```

## Storage I/O Coalescing

NVMe drives support **completion queue interrupt coalescing** via the `Set Features` admin command. Completions accumulate until a threshold count or time expires. At low queue depths this is usually disabled (to minimize latency); at high queue depths it reduces doorbell overhead.

## NAPI: Software-Level Coalescing

Linux's **NAPI** (covered in earlier lessons) is a software form of coalescing: after the first interrupt, further interrupts for that queue are disabled, and the driver polls the queue in a budget-limited batch — achieving the same batching effect as hardware coalescing without requiring hardware support.

## Interview Answer

> **Q: What is interrupt coalescing and why does it matter?**
>
> "Interrupt coalescing delays generating an interrupt until either N completions have accumulated or a timeout expires, then handles all of them in one ISR entry. This trades a small increase in latency for a large reduction in interrupt overhead, preventing interrupt storms at high I/O rates and dramatically increasing throughput."
