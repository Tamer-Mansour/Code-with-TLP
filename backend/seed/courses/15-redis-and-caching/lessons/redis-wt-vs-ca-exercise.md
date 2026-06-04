# Write-Through vs Cache-Aside: Consistency Comparison

Cache-aside and write-through look similar on the surface — both cache objects and serve reads from memory. But they differ fundamentally in **when** the cache is populated and how they handle writes.

This exercise builds both caches side by side so you can observe their behavior directly.

## The two patterns

### Cache-Aside (Lazy Loading)

- Read: check cache first. On miss, fetch from DB, populate cache, return value.
- Write: update DB, then **delete** (invalidate) the cache entry. The next read will repopulate it.
- Result: cache can be **stale** between a write and the next read.

### Write-Through

- Write: update DB **and** cache synchronously in the same operation.
- Read: check cache first. On miss, fetch from DB and populate cache.
- Result: cache always contains the latest written value for any key that has been written.

## Commands

- `WRITE key value` — write to the shared database. Write-through also updates its cache immediately. Cache-aside invalidates (deletes) its cache entry.
- `READ_WT key` — read using the write-through cache. Print `WT: HIT value` or `WT: MISS value`.
- `READ_CA key` — read using the cache-aside cache. Print `CA: HIT value` or `CA: MISS value`.

Both caches share the same underlying in-memory database.

## Example

Input:
```
WRITE user:1 alice
READ_WT user:1
READ_CA user:1
WRITE user:1 bob
READ_WT user:1
READ_CA user:1
READ_CA user:2
READ_WT user:2
```

Output:
```
WT: HIT alice
CA: MISS alice
WT: HIT bob
CA: MISS bob
CA: MISS None
WT: MISS None
```

Key observations:
- After `WRITE user:1 alice`, the write-through cache immediately contains `alice`. The cache-aside cache is empty — it only populates on first read.
- After `WRITE user:1 bob`, cache-aside invalidates its entry. Both caches miss on first access to `user:2`.

## Further reading

- [Caching at Scale with Redis (Redis Inc. PDF)](https://redis.io/wp-content/uploads/2021/12/caching-at-scale-with-redis-updated-2021-12-04.pdf) — Chapter on write strategies and consistency trade-offs
- [Database Caching Strategies Using Redis (AWS Whitepaper)](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/database-caching-strategies-using-redis.pdf) — Canonical comparison of lazy loading vs write-through with diagrams
