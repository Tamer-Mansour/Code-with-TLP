# map vs unordered_map: Which to Choose

Both containers store key–value pairs. The decision between them is one of the most common design questions in C++ interviews. The short answer: prefer `unordered_map` for raw speed, `map` when you need order or range queries.

## Side-by-Side Comparison

| Property | `std::map` | `std::unordered_map` |
|----------|-----------|---------------------|
| Underlying structure | Red-black tree | Hash table |
| Key requirement | Comparable (`<`) | Hashable + equality |
| Lookup complexity | O(log N) | O(1) average, O(N) worst |
| Insert complexity | O(log N) | O(1) average |
| Erase complexity | O(log N) | O(1) average |
| Iteration order | Ascending by key | Unspecified |
| Range queries | Yes (`lower_bound`) | No |
| Memory per element | ~32–48 bytes (tree node + 3 pointers + color) | ~1–2× value size + bucket overhead |
| Cache friendliness | Poor (pointer chasing) | Better (flat bucket array) |
| Header | `<map>` | `<unordered_map>` |

## When to Choose `std::map`

Use `std::map` when:

1. **You need sorted iteration** — reporting data alphabetically, sorted by timestamp, etc.
2. **You need range queries** — "find all keys between A and B" via `lower_bound`/`upper_bound`.
3. **The key type has no good hash** — any `operator<` is sufficient; hashing is not required.
4. **You need guaranteed O(log N) worst-case** — in real-time systems where occasional O(N) rehash spikes are unacceptable.
5. **The map is small (< ~1000 elements)** — the log factor is negligible; the code clarity benefit of ordering may outweigh hash overhead.

```cpp
// Range query: events between timestamps 100 and 200
std::map<int, Event> timeline;
auto start = timeline.lower_bound(100);
auto end   = timeline.upper_bound(200);
for (auto it = start; it != end; ++it) { /* ... */ }
```

## When to Choose `std::unordered_map`

Use `std::unordered_map` when:

1. **Throughput matters** — O(1) average beats O(log N) once N is large enough.
2. **You do not need sorted keys** — word frequency counts, caches, memoisation tables.
3. **You can guarantee a good hash** — built-in types (int, size_t, string) all have quality standard hashes.
4. **You want to reserve capacity up-front** — `reserve()` eliminates rehashes in tight loops.

```cpp
// Memoisation table — O(1) lookup beats O(log N)
std::unordered_map<int, long long> memo;
memo.reserve(100000);
```

## Performance Crossover

In practice, on modern hardware:

- For N < ~100, both containers are so fast the difference is noise.
- For N ~ 10 000, `unordered_map` is typically **3–10× faster** for random-key lookups.
- Cache effects dominate: `unordered_map`'s flat bucket array benefits from prefetching; `map`'s tree causes pointer-chasing cache misses.

A rough benchmark shape (lookups per second, string keys):

```
N = 1 000    |  map: 15M/s  |  unordered_map: 40M/s
N = 100 000  |  map:  8M/s  |  unordered_map: 35M/s
N = 1 000 000|  map:  4M/s  |  unordered_map: 28M/s
```

(Numbers are illustrative; actual results depend on hardware and key type.)

## The Sorted-Vector Alternative

For read-heavy workloads with a fixed key set, a sorted `vector<pair<K,V>>` + `std::lower_bound` often beats both:

```cpp
// Build once, query many times
std::vector<std::pair<std::string, int>> table = { /* ... */ };
std::sort(table.begin(), table.end());

// Binary search: O(log N) with excellent cache behaviour
auto it = std::lower_bound(table.begin(), table.end(),
                            std::make_pair(std::string("key"), 0));
```

This trades insertion speed for superior cache locality during lookups — all data is contiguous.

## Decision Flowchart

```
Need key–value association?
  ├─ Need sorted order or range queries?  ──► std::map
  ├─ Key type has no < but has hash?       ──► std::unordered_map
  ├─ Key set is fixed, read-heavy?         ──► sorted vector + lower_bound
  └─ General case, max lookup speed?       ──► std::unordered_map
```

## Common Mistakes

- **Using `map` out of habit** — many engineers reach for `map` by default. Audit hot paths.
- **Using `unordered_map` without `reserve`** — rehashing in a tight insert loop degrades the amortised O(1) guarantee.
- **Assuming `unordered_map` is always faster** — with a pathological hash, or on very small N, `map` can win.

> **Interview answer:** Default to `unordered_map` for O(1) average lookup when you do not need ordering; switch to `map` when you need sorted iteration, range queries (`lower_bound`), or a worst-case O(log N) guarantee free of hash-flooding risk.
