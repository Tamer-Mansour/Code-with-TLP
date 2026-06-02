# Container Complexity and Cache Behavior

Choosing the right container is not just about Big-O complexity on paper — it is about what happens in the processor's cache. A container with a worse asymptotic bound can outperform a theoretically superior one when the data is laid out contiguously in memory and the hardware prefetcher can do its job.

## The Full Complexity Table

| Container | Index | Front insert | Back insert | Mid insert | Find (unsorted) | Find (key) | Memory layout |
|-----------|:-----:|:------------:|:-----------:|:----------:|:---------------:|:----------:|:-------------:|
| `vector` | O(1) | O(N) | O(1)* | O(N) | O(N) | — | Contiguous |
| `array` | O(1) | — | — | — | O(N) | — | Contiguous |
| `deque` | O(1) | O(1)* | O(1)* | O(N) | O(N) | — | Segmented |
| `list` | O(N) | O(1) | O(1) | O(1)** | O(N) | — | Scattered |
| `forward_list` | O(N) | O(1) | O(N) | O(1)** | O(N) | — | Scattered |
| `map` | — | — | — | O(log N) | — | O(log N) | Scattered (tree) |
| `set` | — | — | — | O(log N) | — | O(log N) | Scattered (tree) |
| `unordered_map` | — | — | — | O(1)* | — | O(1)* | Flat + chains |
| `unordered_set` | — | — | — | O(1)* | — | O(1)* | Flat + chains |

\* amortised  ** given an iterator

## Cache Behavior in Practice

Modern CPUs execute memory accesses in 64-byte cache lines. When a program reads element N, the CPU automatically fetches elements N+1 through N+7 into the cache — this is the **spatial prefetcher**. Contiguous containers exploit this; scattered containers waste it.

### Vector Sequential Scan

```
Cache line: [e0|e1|e2|e3|e4|e5|e6|e7] → loaded in one fetch
Vector:      ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑
              All hit L1 cache after first miss
```

A sequential scan over `vector<int>` can achieve close to **memory bandwidth** — the bottleneck is DRAM throughput, not instruction execution.

### List Sequential Scan

```
Node 0 ──ptr──► Node 1 ──ptr──► Node 2
   (addr 0x1000)  (addr 0x5F30)  (addr 0x2A80)
```

Each `next` pointer dereference is likely a cache miss if the list was built incrementally. On a modern machine that is 50–200 ns per miss — catastrophic in a tight loop.

### Measured Reality (N = 1 000 000 ints, sequential sum)

| Container | Time (approx) | Cache misses |
|-----------|:-------------:|:------------:|
| `vector<int>` | ~1 ms | Near zero |
| `deque<int>` | ~2 ms | Low |
| `list<int>` | ~20 ms | ~1M misses |

The `list` is 20× slower than `vector` despite identical O(N) algorithmic complexity.

## The Rule of Cache-Friendliness

> Prefer containers with contiguous or near-contiguous layout for data that is accessed sequentially or repeatedly.

- `vector` > `deque` > `list` for sequential access throughput.
- `array` = `vector` for sequential access (same layout).
- `unordered_map` > `map` for lookup-heavy workloads because the bucket array is flat.

## Iterator Invalidation Cheatsheet

Operations that invalidate iterators/references are important to know under pressure:

| Container | Insert | Erase | Realloc |
|-----------|--------|-------|---------|
| `vector` | All iterators if realloc; only after point of insert otherwise | All after point of erase | All iterators + references |
| `deque` | All iterators if front/back insert; all otherwise | All |  — |
| `list` | None | Only erased node | — |
| `map` / `set` | None | Only erased node | — |
| `unordered_map` | All if rehash | Only erased node | All on rehash |

## Memory Overhead Per Element

```
vector<int>       :  4 bytes/element + 24-byte header
list<int>         : 20 bytes/element (4 data + 8 prev + 8 next) + allocator overhead
map<int,int>      : ~48 bytes/element (2 ints + 3 pointers + color + allocator)
unordered_map<int>: ~8–16 bytes/element (key+value) + ~8 bytes/bucket pointer
```

For a million integers, `list` uses ~5× more memory than `vector`, and most of that extra memory is pointer overhead that the CPU must load but never "processes."

## Choosing Under Pressure: A Decision Matrix

```
Access pattern?
  ├─ Random access by index   → vector or array
  ├─ Key lookup               → unordered_map (fast) or map (ordered)
  ├─ Sequential scan only     → vector (cache-optimal)
  └─ Both ends push/pop       → deque

Mutation pattern?
  ├─ Back-only insert/erase   → vector
  ├─ Both ends insert/erase   → deque
  ├─ Mid-sequence (by key)    → map / unordered_map
  └─ Mid-sequence (arbitrary) → list (only if you have the iterator)

Uniqueness required?
  ├─ Sorted unique set        → set
  └─ Fast unique set          → unordered_set
```

## Worked Example: Profiling a Hot Loop

```cpp
// Slow: pointer-chasing list
std::list<Packet> packets;
long total = 0;
for (const auto& p : packets) total += p.size;   // cache miss per element

// Fast: contiguous vector
std::vector<Packet> packets;
long total = 0;
for (const auto& p : packets) total += p.size;   // prefetcher-friendly
```

If you profile and find the list version bottlenecked on memory latency, migrating to `vector` (or `vector` of indices) is often a 5–20× speedup with no algorithmic change.

> **Interview answer:** Big-O complexity describes algorithm behaviour but ignores constants; in practice, `vector` dominates for sequential workloads because contiguous memory enables hardware prefetching, while `list` and tree-based containers cause one cache miss per element access, costing 50–200 ns each on modern hardware.
