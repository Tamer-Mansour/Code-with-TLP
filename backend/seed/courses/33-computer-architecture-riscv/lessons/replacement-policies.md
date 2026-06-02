# Replacement Policies: LRU, FIFO, Random

When a cache miss occurs and the target set is full, the hardware must choose a **victim line** to evict. The **replacement policy** makes that choice. The goal is to evict the line least likely to be needed again. No policy is perfect without knowing the future, so each is a heuristic with different trade-offs.

## LRU (Least Recently Used)

**LRU** evicts the line that was accessed furthest in the past. It exploits temporal locality: if a line has not been used for a long time, it is probably not needed soon.

### Tracking LRU Order

For an N-way set, hardware maintains a recency ordering of the N ways. On each access:
- Hit: promote the accessed way to MRU (Most Recently Used) position.
- Miss + eviction: evict the LRU way, load new block, mark it MRU.

For 2-way, a single bit per set suffices. For 4-way, 6 bits encode the full permutation. For 8-way or more, exact LRU becomes expensive — most real processors use **pseudo-LRU** (PLRU), a tree-based approximation that needs only N−1 bits.

```
2-way LRU example (bit = 0 means Way 0 is LRU):
  Access Way 0: bit = 1  (Way 1 is now LRU)
  Access Way 1: bit = 0  (Way 0 is now LRU)
  Miss:         evict Way 0 (current LRU)
```

### When LRU Fails: Thrashing

If the working set is N+1 blocks and the set has N ways, LRU cycles through all N+1 blocks and misses on every access — **LRU thrashing**. This is a well-known pathological case.

## FIFO (First In, First Out)

**FIFO** evicts the line that has been in the cache the longest, regardless of access recency. It is simpler than LRU — only the insertion order needs tracking, not the full access order.

```
Set state (FIFO queue, left = oldest):
  Load A: [A]
  Load B: [A, B]
  Load C: [A, B, C]  (set full, 3-way)
  Access A: [A, B, C]  ← no change! A stays in position
  Load D: evict A → [B, C, D]
```

Note the difference from LRU: even though `A` was just accessed, FIFO evicts it because it was inserted first.

FIFO can suffer from **Belady's anomaly**: adding more cache lines can sometimes *increase* the miss rate for certain access patterns. LRU is immune to Belady's anomaly.

## Random

**Random replacement** selects a victim uniformly at random. It requires no state tracking — hardware uses a simple counter or LFSR (linear feedback shift register).

- Average performance is surprisingly close to LRU on real workloads.
- No pathological worst case: adversarial access patterns cannot reliably cause thrashing.
- Used in ARM Cortex-A cores (with a configurable pseudo-random policy).

## Optimal (OPT / Belady's)

**OPT** evicts the block that will be accessed furthest in the future. It is not implementable in hardware (requires knowledge of future accesses) but serves as a theoretical upper bound for hit-rate comparisons and cache simulator benchmarks.

## Summary Comparison

| Policy  | Principle | State overhead | Belady anomaly? | Notes |
|---------|-----------|----------------|-----------------|-------|
| LRU     | Evict least recently accessed | High (N! orderings) | No | Best on typical workloads; hardware uses PLRU |
| FIFO    | Evict oldest insertion | Low (queue pointer) | Yes | Simple; slightly worse than LRU |
| Random  | Evict random way | Minimal (LFSR) | No | Robust; competitive on real workloads |
| OPT     | Evict furthest future use | Impossible online | No | Theoretical optimum |

## Practical Reality

- **L1/L2** caches on modern CPUs typically use pseudo-LRU — a good approximation with manageable hardware cost.
- **L3** caches often use more complex policies (Intel uses an adaptive replacement policy similar to ARC) because the stakes are higher and the larger way count makes true LRU impractical.
- **TLBs** often use random or FIFO because they are fully associative and even pseudo-LRU would be expensive.

```c
// Programmer tip: access patterns matter
// This thrashes a 4-way cache if arrays are cache-set aliases:
for (int i = 0; i < N; i++)
    process(a[i], b[i], c[i], d[i], e[i]);  // 5 streams, 4 ways → LRU thrashes

// Fix: software prefetch or restructure data to reduce streams
```

> **Interview answer:** LRU evicts the least recently used line and performs best on typical workloads; FIFO is simpler but can suffer Belady's anomaly; Random requires no state and is surprisingly competitive. Real CPUs use pseudo-LRU because exact LRU state is too expensive for 8-way or 16-way caches.
