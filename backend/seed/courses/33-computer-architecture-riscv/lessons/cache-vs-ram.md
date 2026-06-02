# Cache vs RAM: Key Differences

Understanding the differences between cache and RAM is foundational for reasoning about program performance, hardware design, and system bottlenecks. They serve the same broad purpose — storing data for the CPU — but differ across nearly every meaningful dimension.

## Technology

- **Cache** is built from **SRAM** (Static RAM). Each bit is stored in a flip-flop made of six transistors. No refresh is needed; data persists as long as power is supplied.
- **RAM** (main memory) is built from **DRAM** (Dynamic RAM). Each bit is stored as a charge in a single capacitor paired with one transistor. The charge leaks away and must be refreshed thousands of times per second, adding latency and complexity.

This fundamental circuit-level difference drives almost every other contrast between the two.

## Comparison Table

| Property          | Cache (SRAM)             | Main Memory (DRAM)       |
|-------------------|--------------------------|--------------------------|
| Technology        | SRAM (6T flip-flop)      | DRAM (1T1C capacitor)    |
| Typical size      | 32 KB – 64 MB            | 4 GB – 128 GB            |
| Access latency    | 1–50 clock cycles        | 150–300 clock cycles     |
| Bandwidth         | Very high (on-die bus)   | Lower (off-chip bus)     |
| Cost per GB       | ~$1,000+ (2024 estimate) | ~$3–6 (2024 estimate)    |
| Location          | On the CPU die           | Separate DIMM module     |
| Managed by        | Hardware automatically   | OS + programmer          |
| Volatility        | Volatile (loses on power off) | Volatile             |
| Refresh needed    | No                       | Yes (~64 ms cycle)       |

## Visibility to the Programmer

The biggest practical difference: **RAM is explicitly addressable; cache is not.**

A programmer writes to memory address `0x10004000` — the hardware decides whether that access hits cache or goes to RAM. The programmer has no direct pointer into L1 or L2. Control happens indirectly, through access patterns that respect locality.

```c
// Cache-friendly: stride-1 traversal (spatial locality)
for (int i = 0; i < N; i++)
    sum += row_major[i];

// Cache-hostile: stride-N traversal (column-major on row-major storage)
for (int j = 0; j < N; j++)
    sum += matrix[j * N + 0];  // Jumps 4*N bytes each step — evicts lines
```

## Capacity vs Speed Trade-off

The reason we have multiple cache levels rather than one giant L1 is physics. Larger memories have longer wire runs and higher capacitance, which slows access. A 32 KB L1 can be placed close enough to the ALU to respond in 3–4 cycles; a 32 MB L3 on the same die takes 30–50 cycles.

This is why the hierarchy exists: each level is a deliberate compromise between size and speed.

## Persistence and Initialization

Both cache and RAM are volatile — they lose their contents when power is removed. However, RAM is initialised by the OS during boot (zeroing pages, loading the OS kernel). Cache initialises implicitly: on first access, data is fetched from RAM or disk into cache lines. There is no explicit "fill the cache" operation in normal programming.

## Common Pitfall: Assuming Cache Transparency

Beginners sometimes assume that because cache is invisible, it does not matter for correctness. This is true for single-threaded code on a simple architecture, but **cache coherence** problems surface in multi-core systems — two cores can hold stale copies of the same cache line with different values. Hardware cache-coherence protocols (MESI, MOESI) handle this, but programmers must still use proper synchronisation primitives to avoid data races.

> **Interview answer:** Cache is small, on-chip SRAM managed by hardware; RAM is large, off-chip DRAM managed by the OS. Cache is ~50x faster but ~200x more expensive per bit, so a hierarchy of cache levels bridges the speed gap at a reasonable cost.
