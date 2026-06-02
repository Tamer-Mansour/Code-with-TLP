# What Is Cache Memory?

Cache memory is a small, fast memory layer placed between the CPU and main memory (RAM). Its job is simple: hold the data and instructions the processor is most likely to need next, so the CPU does not have to wait for the comparatively slow journey to RAM and back.

## The Speed Problem

Modern CPUs execute billions of instructions per second. A typical register-to-ALU operation completes in a fraction of a nanosecond. A read from DRAM, on the other hand, takes 60–100 ns — roughly 200 clock cycles on a 3 GHz processor. Without cache, the CPU would be idle for most of those cycles, waiting for data.

Cache solves this by exploiting two empirically proven patterns in how programs access memory:

- **Temporal locality** — data accessed once is likely to be accessed again soon (loop variables, counters).
- **Spatial locality** — data near a recently accessed location is likely to be needed soon (array elements, sequential instructions).

## The Cache Hierarchy

Modern processors have two to four levels of cache, each larger and slower than the one above it:

| Level | Typical size | Access latency | Location |
|-------|-------------|----------------|----------|
| L1    | 32–64 KB    | 1–5 cycles     | Per-core, on-die |
| L2    | 256 KB – 1 MB | 5–15 cycles  | Per-core, on-die |
| L3    | 4–64 MB     | 30–50 cycles   | Shared across cores, on-die |
| RAM   | 4–128 GB    | 150–300 cycles | Off-chip |

The CPU always checks L1 first, then L2, then L3, then main memory. The first level that contains the requested data supplies it — a **hit**. If no level holds the data, the request falls through to RAM — a **miss**.

## Why Not Just Make RAM Faster?

SRAM (the technology inside cache) is built from six transistors per bit. It is fast but large and expensive. DRAM (used in RAM modules) uses one transistor and one capacitor per bit — much denser and cheaper, but slower because the capacitor must be periodically refreshed.

The cache hierarchy is an engineering compromise: use a small amount of expensive, fast SRAM to satisfy most requests, and use cheap, slow DRAM for the bulk of storage.

## A Concrete Example

Consider a tight loop summing an array:

```c
int sum = 0;
for (int i = 0; i < 1024; i++) {
    sum += arr[i];
}
```

- On the first iteration, `arr[0]` is fetched from RAM. The cache also pulls in the adjacent 64 bytes (a full **cache line**) — `arr[0]` through `arr[15]` for 4-byte integers.
- Iterations 1–15 find their data already in cache: 15 hits for the cost of one miss.
- The loop variable `sum` lives in a register but, if spilled, benefits from temporal locality.
- This access pattern is as cache-friendly as it gets; performance is close to peak throughput.

## Key Concepts at a Glance

- Cache is SRAM; RAM is DRAM. SRAM is fast, small, and expensive.
- The hierarchy (L1 → L2 → L3 → RAM) trades size for speed at each level.
- Temporal and spatial locality are why cache works so well in practice.
- A **cache hit** returns data without touching RAM; a **cache miss** forces a slower RAM access.

> **Interview answer:** Cache memory is a small, fast SRAM buffer between the CPU and main RAM that exploits temporal and spatial locality to reduce average memory-access latency from ~200 cycles to ~4 cycles.
