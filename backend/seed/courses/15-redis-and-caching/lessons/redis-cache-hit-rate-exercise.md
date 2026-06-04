# Cache Hit Rate Analyzer

Every caching system lives or dies by its **hit rate** — the percentage of read requests served from cache rather than from the slow backing store. A hit rate below 80% usually means either the cache is too small, the TTL is too short, or the workload is not cache-friendly.

In this exercise you will simulate the **cache-aside (lazy loading)** pattern and compute the hit rate after a series of reads.

## How cache-aside works

1. On `READ key`: check the cache first.
2. **Hit**: return the cached value.
3. **Miss**: fetch from the database (simulated as `key + "_val"`), store in cache, return the value.
4. When the cache is full, evict the oldest inserted key (FIFO on capacity).
5. A cached entry expires after `TTL` operations have elapsed since it was inserted.

## Input format

```
N
TTL
READ key1
READ key2
...
```

- Line 1: cache capacity `N` (1 ≤ N ≤ 100)
- Line 2: TTL in number of operations (a key expires once this many operations have passed since insertion)
- Remaining lines: `READ key` commands

## Output format

For each `READ`, print:
- `HIT: <value>` or `MISS: <value>`

After all reads, print one summary line:

```
Total: X, Hits: Y, Misses: Z, Hit Rate: P%
```

where `P` is rounded to 1 decimal place.

## Example

```
Input:
2
3
READ user:1
READ user:2
READ user:1
READ user:3
READ user:1
READ user:2

Output:
MISS: user:1_val
MISS: user:2_val
HIT: user:1_val
MISS: user:3_val
MISS: user:1_val
MISS: user:2_val
Total: 6, Hits: 1, Misses: 5, Hit Rate: 16.7%
```

Walkthrough:
- Op 1: `user:1` not in cache → MISS, insert. Cache: `{user:1 (op1), user:2 ...}`
- Op 2: `user:2` not in cache → MISS, insert. Cache full.
- Op 3: `user:1` in cache, age = 3-1 = 2 < TTL(3) → HIT.
- Op 4: `user:3` not in cache. Evict oldest (`user:1`, inserted op 1). MISS.
- Op 5: `user:1` not in cache (was evicted) → MISS.
- Op 6: `user:2` in cache, age = 6-2 = 4 ≥ TTL(3) → expired. MISS.
