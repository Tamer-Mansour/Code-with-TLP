# Bus Width and Throughput

Bus **width** is the number of parallel data lines — bits that travel simultaneously in a single clock cycle. **Throughput** is the sustained rate at which bytes flow across the bus. Understanding how these two figures interact is essential for any system-level design or performance analysis.

## The Basic Formula

```
Throughput = (Bus Width in bits / 8) × Bus Clock Frequency
```

| Bus standard | Width (bits) | Clock (MHz) | Peak throughput |
|-------------|-------------|-------------|-----------------|
| ISA (8-bit)  | 8           | 8           | 8 MB/s          |
| ISA (16-bit) | 16          | 8           | 16 MB/s         |
| PCI          | 32          | 33          | 133 MB/s        |
| PCI-X        | 64          | 133         | 1066 MB/s       |
| DDR4 SDRAM   | 64          | 3200 (data) | ~25,600 MB/s    |

**Interview answer:** Bus throughput equals (width in bytes) × (clock frequency). Doubling the width or the clock doubles peak throughput — but peak is rarely sustained because of overhead cycles.

## Effective vs. Peak Throughput

Every bus transaction has **overhead** — address setup, arbitration, turnaround cycles, wait states. These cycles carry no data, so effective throughput is always lower than peak:

```
Effective Throughput = (Data Bytes per Transaction) / (Total Cycles per Transaction) × Clock
```

**Example:** A 32-bit PCI bus at 33 MHz transfers 4 bytes per clock. A memory burst read of 16 bytes (4 beats) takes roughly 10 cycles total (1 address + 1 turnaround + 4 data + 4 wait states = 10). Effective rate = 16 bytes / 10 cycles × 33 MHz ≈ 52 MB/s — far below the theoretical 133 MB/s.

## Burst Transfers

**Burst mode** amortizes the address and overhead across multiple data beats. Instead of issuing a new address for every 4 bytes, the bus master sends one address and then transfers N consecutive words at full data rate:

```
Without burst:  [ADDR][DATA] [ADDR][DATA] [ADDR][DATA]  (3 × overhead)
With burst:     [ADDR][DATA][DATA][DATA]                 (1 × overhead)
```

Cache line fills use burst transfers — a cache miss loads a full 64-byte line in one burst rather than 16 individual 4-byte transactions.

## Bus Width vs. CPU Word Size

The bus width and the CPU's internal word size can differ:

- **Narrower bus than CPU** — the CPU must split a single 64-bit word into multiple bus transactions. This is called a **split transaction** and adds latency.
- **Wider bus than CPU** — extra lines go unused unless the system can aggregate multiple devices (e.g., two 32-bit DIMMs forming one 64-bit memory channel).

The x86 Pentium had a 64-bit external data bus but a 32-bit internal register file — wider external bus to feed the cache faster.

## Worked Example: Memory Bandwidth Calculation

A system has a DDR4-3200 memory module with a 64-bit (8-byte) data bus running at an effective rate of 3200 MT/s (million transfers per second, doubled from 1600 MHz due to DDR):

```
Peak bandwidth = 8 bytes × 3200 MT/s = 25,600 MB/s ≈ 25.6 GB/s
```

A dual-channel configuration doubles this to ~51.2 GB/s by running two 64-bit channels in parallel — effectively 128-bit width.

## Common Pitfalls

- **Confusing MHz with MT/s**: DDR memory transfers on both edges of the clock (Double Data Rate), so 1600 MHz yields 3200 MT/s.
- **Ignoring overhead**: quoting peak throughput in an interview without mentioning efficiency looks naive.
- **Assuming linear scaling**: adding more width helps only if the bottleneck is the bus, not the CPU or memory device itself.

## Key Takeaway

Bus throughput scales with both width and frequency, but real systems achieve a fraction of peak due to protocol overhead. Burst transfers are the primary tool for recovering efficiency — they reduce per-byte overhead by spreading fixed costs across multiple data beats.
