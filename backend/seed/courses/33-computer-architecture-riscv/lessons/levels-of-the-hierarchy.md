# Levels: Registers, Cache, RAM, Disk

The memory hierarchy is not a theoretical construct — it is a concrete set of physical components with very different characteristics. Understanding each level, what it is made of, how fast it is, and why it exists at that level of the hierarchy is essential for reasoning about program performance.

## Registers

Registers sit at the top of the hierarchy, inside the CPU itself.

- **Technology:** Flip-flops (combinational CMOS logic)
- **Access time:** Sub-nanosecond (effectively 0 extra cycles)
- **Capacity:** Typically 32 × 64-bit general-purpose registers in RISC-V (x0–x31)
- **Managed by:** The compiler (or the programmer in assembly)

The CPU can only perform arithmetic on data that is in a register. Every load/store instruction is explicitly moving data between a register and memory. There is no automatic promotion — the compiler must schedule which values live in registers and when they are spilled to the stack.

## Cache Memory (L1, L2, L3)

Cache is SRAM (static RAM) integrated on the same silicon die as the CPU.

- **L1 cache:** Closest to the execution units. Split into separate instruction (I-cache) and data (D-cache) caches. Typically 32–64 KB per core. Latency: 1–5 cycles.
- **L2 cache:** Unified (instructions + data), per core. Typically 256 KB – 1 MB. Latency: 6–20 cycles.
- **L3 cache (Last-Level Cache, LLC):** Shared across all cores on the chip. Typically 4–64 MB. Latency: 20–60 cycles.

Cache is invisible to the programmer in most ISAs; the hardware controller decides what to keep, evict, and fetch automatically based on access patterns.

```asm
# RISC-V: this load may hit L1, L2, L3, or DRAM — the ISA doesn't know
lw  a0, 0(a1)   # load word at address in a1 into a0
```

## Main Memory (DRAM)

DRAM (dynamic RAM) is the "working memory" of the system — what the OS calls RAM.

- **Technology:** One capacitor + one transistor per bit; must be refreshed every ~64 ms
- **Capacity:** 4 GB – 512 GB in typical systems
- **Latency:** 60–100 ns (roughly 200–300 CPU cycles at 3 GHz)
- **Bandwidth:** 25–100 GB/s (DDR4/DDR5 with multiple channels)
- **Managed by:** The operating system's virtual memory subsystem

When a cache miss occurs and the requested cache line is not in any cache level, the memory controller fetches a 64-byte cache line from DRAM. This is called a **last-level cache miss** and is one of the most expensive operations a program can trigger repeatedly.

## Secondary Storage (SSD / HDD)

Storage devices hold data that survives power loss (non-volatile).

| Device | Technology | Latency | Typical Size |
|--------|-----------|---------|--------------|
| NVMe SSD | NAND flash | 50–200 µs | 256 GB – 8 TB |
| SATA SSD | NAND flash | 100–500 µs | 128 GB – 4 TB |
| HDD | Magnetic platters | 3–10 ms | 500 GB – 20 TB |

The OS uses secondary storage for:
1. The file system (persistent data)
2. The **swap space** (virtual memory pages evicted from DRAM)

## Visualizing the Latency Cliff

If one CPU cycle = 1 second, the analogy becomes:

- Register access: **instantly**
- L1 cache: **3 seconds**
- L2 cache: **15 seconds**
- L3 cache: **60 seconds**
- DRAM: **6 minutes**
- NVMe SSD: **~2 days**
- HDD: **~6 months**

This "latency cliff" illustrates why cache misses that fall through to DRAM — let alone to disk — are so costly relative to CPU speed.

## Common Pitfalls

- **Forgetting L3 is shared:** In a multi-core system, heavy cache usage by one core evicts another core's data from the LLC, causing unexpected slowdowns.
- **Confusing bandwidth with latency:** DRAM has high bandwidth (sequential reads are fast) but high latency for random access. Sequential loops are much friendlier to the hierarchy than pointer-chasing.
- **Swap kills performance:** When the OS starts paging to SSD (let alone HDD), effective memory latency jumps by 1000× or more.

## Worked Example

A program accesses a 64-byte struct repeatedly inside a tight loop.

```c
for (int i = 0; i < 1000000; i++) {
    result += obj.value;   // obj is 64 bytes — fits in one cache line
}
```

On the first iteration, `obj` is fetched from DRAM (~100 ns). For all subsequent 999,999 iterations it is in L1 cache (~1 ns). The total cost is dominated by that single miss, making the loop nearly as fast as if DRAM did not exist.

> **Interview answer:** The hierarchy has registers (sub-ns, compiler-managed), L1/L2/L3 SRAM caches (1–60 cycles, hardware-managed), DRAM main memory (200–300 cycles), and storage (millions of cycles); each level trades speed for capacity and cost.
