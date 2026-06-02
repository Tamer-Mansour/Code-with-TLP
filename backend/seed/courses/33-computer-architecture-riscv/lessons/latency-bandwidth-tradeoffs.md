# Latency vs Bandwidth Trade-offs

Latency and bandwidth are the two fundamental metrics of memory performance, and they are often confused or conflated. Understanding the difference — and why a memory subsystem can have high bandwidth yet high latency simultaneously — is critical for writing fast code and reasoning about system bottlenecks.

## Definitions

**Latency** is the time from when a request is issued to when the first byte of data is available. It is a measure of how fast a single, isolated request can be satisfied.

**Bandwidth** (also called throughput) is the rate at which data can be transferred, usually measured in GB/s. It reflects how much data can be moved per unit time when the channel is kept busy with a stream of requests.

| Metric | Unit | Analogy |
|--------|------|---------|
| Latency | ns, µs, ms | Time to get the first item from a store |
| Bandwidth | GB/s, MB/s | Number of items that flow through the checkout line per minute |

## Why They Are Independent

A system can have high bandwidth but high latency. Consider DDR5 DRAM:

- **Latency:** ~70 ns for a random access (the memory controller sends a row activate command, waits for the row to open, then reads the column — this sequential protocol cannot be pipelined for a single address)
- **Bandwidth:** 50–100 GB/s for sustained sequential reads (many concurrent outstanding requests fill the bus continuously)

Conversely, CPU registers have near-zero latency but effectively zero bandwidth for random access patterns (there is no "stream" — only a handful of values at a time).

## Sequential vs Random Access

The distinction shapes how latency and bandwidth manifest in practice:

```c
// Sequential — bandwidth-bound: hardware prefetcher hides latency
for (int i = 0; i < N; i++) sum += arr[i];

// Random — latency-bound: each access depends on previous result
Node* p = head;
while (p) { sum += p->val; p = p->next; }  // each p->next is unknown until fetched
```

In the sequential case, the CPU's hardware prefetcher detects the stride and issues DRAM requests before the data is needed, keeping the memory bus saturated (bandwidth-bound). In the random case, each request stalls until complete because the next address is unknown — latency is exposed directly (latency-bound).

## Bandwidth-Latency Product (Little's Law)

From queueing theory, the maximum achievable throughput satisfies:

```
Bandwidth = Concurrency / Latency
```

Or equivalently, to sustain full bandwidth you need:

```
Concurrency = Bandwidth × Latency
```

**Example:** DDR4 offers 40 GB/s of bandwidth and 80 ns latency.

```
Concurrency = 40 GB/s × 80 ns = 40 × 10⁹ B/s × 80 × 10⁻⁹ s = 3200 bytes
```

With 64-byte cache lines that means you need **50 outstanding cache line requests** simultaneously to saturate the memory bus. A single-threaded pointer-chasing loop can issue at most 1 outstanding request at a time — it gets only 1/50 of the available bandwidth and is completely latency-bound.

## Implications for Code

| Access Pattern | Bottleneck | Fix |
|---------------|-----------|-----|
| Sequential array scan | Bandwidth | Use SIMD; ensure prefetcher fires |
| Random pointer chasing | Latency | Restructure to improve locality; use arrays not linked lists |
| Many short messages | Latency per message | Batch requests; use larger transfers |
| Large data copy | Bandwidth | Use `memcpy` (uses non-temporal stores to avoid polluting cache) |

## Non-Temporal Stores

When writing large blocks of data that will not be read back soon, use non-temporal (streaming) stores to bypass the cache:

```cpp
#include <immintrin.h>
// Store 256 bits without allocating a cache line
_mm256_stream_si256((__m256i*)dst, data);
```

This avoids the **read-for-ownership** penalty where a cache line must be fetched from DRAM before it can be modified, doubling effective write bandwidth for large sequential writes.

## Worked Example: Estimating Bottleneck

A function scans a 256 MB array of 32-bit integers sequentially.

- Array size: 256 MB
- DRAM bandwidth: 40 GB/s
- DRAM latency: 80 ns

Sequential scan is bandwidth-bound (hardware prefetch hides latency). Estimated time:

```
Time = 256 MB / 40 GB/s = 256 / 40,960 s ≈ 6.25 ms
```

If the same data were accessed randomly (e.g., indirect index scan):

```
Accesses = 256 MB / 4 bytes = 64 million
Time = 64 × 10⁶ × 80 ns = 5.12 seconds
```

That is an 800× difference for the same data and the same memory — purely due to the latency vs bandwidth distinction.

## Common Pitfalls

- **Optimizing bandwidth when the workload is latency-bound**: adding more DRAM channels does not help pointer-chasing loops.
- **Ignoring prefetch effectiveness**: hardware prefetchers handle simple strides well but fail on irregular patterns.
- **Cache pollution from streaming writes**: writing large buffers fills the cache with data that will never be re-read, evicting useful data.

> **Interview answer:** Latency is the time to receive the first byte of a single request; bandwidth is the sustained data rate across many concurrent requests. Random access is latency-bound; sequential access is bandwidth-bound, and hardware prefetchers can hide latency for predictable strides.
