# Quiz: Caching Patterns

Verify your understanding of cache-aside, write-through, write-behind, TTLs, and eviction policies.

## Question 1

In the cache-aside pattern, when does the cache get populated?

[ ] On every write to the database
[x] On a cache miss during a read operation
[ ] During application startup (cache warming)
[ ] When the TTL expires

## Question 2

A write-through cache and a cache-aside cache both start empty. You execute `WRITE user:1 alice` followed immediately by `READ user:1`. Which cache serves the read from memory without hitting the database?

[x] Write-through cache
[ ] Cache-aside cache
[ ] Both caches serve the read from memory
[ ] Neither — both must hit the database on first read

## Question 3

Which eviction policy should you choose when Redis is used as a pure cache and you want to keep the most frequently accessed keys in memory?

[ ] noeviction
[ ] volatile-ttl
[x] allkeys-lfu
[ ] allkeys-random

## Question 4

You have a Redis cache with `maxmemory-policy allkeys-lru`. What happens when Redis reaches its memory limit and a new key is written?

[ ] Redis returns an OOM error and rejects the write
[ ] Redis flushes the entire cache
[x] Redis evicts the least recently used key before inserting the new one
[ ] Redis extends its memory limit automatically

## Question 5

Adding a small random jitter to TTL values (e.g., `base_ttl + random(0, 30)`) solves which problem?

[ ] Hot key overloading a single cluster node
[ ] Cache-aside write-path staleness
[x] Synchronized cache expiration causing a thundering herd at the same instant
[ ] Memory fragmentation in Redis

## Question 6

Write-behind (write-back) caching accepts writes into Redis first and persists to the database asynchronously. What is the main risk of this approach?

[x] Data written to Redis but not yet flushed to the database is lost if Redis crashes
[ ] Writes become slower because they must traverse two storage layers
[ ] The cache may serve stale reads after a write
[ ] The database can get ahead of the cache and cause consistency errors

## Question 7

Negative caching stores a sentinel value for keys that do not exist in the database. Why is this useful?

[ ] It prevents memory fragmentation
[ ] It enables faster AOF rewriting
[x] It stops repeated database queries for missing keys, protecting against cache miss flooding
[ ] It ensures the cache and database are always consistent

## Question 8

Your application stores user session objects that are updated on every page view. Which caching pattern introduces the least write latency while keeping the cache consistent?

[ ] Write-through (sync update to cache and DB on every write)
[ ] Cache-aside with invalidation on write
[x] Write-behind (async flush) with short TTL as a safety net
[ ] Read-through with periodic refresh

## Question 9

According to Redis documentation, `noeviction` is the correct `maxmemory-policy` for which use case?

[ ] A pure cache with frequently changing hot keys
[ ] An LRU cache with bounded memory
[x] Redis used as a primary data store where data loss from eviction is unacceptable
[ ] A leaderboard with millions of entries
