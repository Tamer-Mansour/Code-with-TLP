# Cache-aside, Write-through, and TTLs

Putting Redis in front of a slow backend is the most common reason people pick it up. There are a few canonical patterns; pick the one that matches your read/write ratio and consistency needs.

## Cache-aside (lazy)

The most popular pattern. The application code orchestrates.

```python
def get_user(uid):
    v = redis.get(f"user:{uid}")
    if v is not None:
        return json.loads(v)
    row = db.fetch_one("SELECT ... FROM users WHERE id=%s", uid)
    redis.set(f"user:{uid}", json.dumps(row), ex=300)   # 5 min TTL
    return row
```

On write you **invalidate** the key:

```python
def update_user(uid, fields):
    db.execute("UPDATE users SET ... WHERE id=%s", uid)
    redis.delete(f"user:{uid}")
```

Pros: Simple. Cache contents reflect actual reads.
Cons: Stale-write window if writers can't always invalidate. First read after invalidation eats the slow path.

## Write-through

Writes go through Redis, which writes to the backing store synchronously.

```python
def update_user(uid, data):
    db.execute("UPDATE users SET ... WHERE id=%s", uid)
    redis.set(f"user:{uid}", json.dumps(data), ex=300)
```

Effectively cache-aside where the write side maintains the cache instead of invalidating. Use when reads always want the latest write.

## Write-behind (write-back)

Writes go to Redis immediately and propagate to the backend asynchronously. Throughput is huge; durability is weaker. Used for high-volume counters where you can tolerate a few seconds of "lost updates" if Redis crashes.

## TTL strategy

A TTL bounds staleness even when invalidation is missed. Useful TTL choices:

- **Fresh small data** — seconds to minutes.
- **User profile / settings** — 5–30 minutes.
- **Catalog / config** — hours.
- **Static reference data** — days, with explicit invalidation on updates.

Add a small **jitter**: a base TTL ± 10% to spread expirations and avoid synchronized cache misses.

```python
redis.set(key, val, ex=300 + random.randint(0, 30))
```

## Negative caching

Cache "this doesn't exist" too — otherwise a stream of queries for missing IDs hammer the DB.

```python
if v == b"__null__":
    return None
if v is not None:
    return json.loads(v)
row = db.fetch_one(...)
redis.set(key, json.dumps(row) if row else "__null__", ex=60)
```

Use a shorter TTL for negatives.

## maxmemory policies

When Redis fills up, it evicts. Set the policy explicitly:

```
maxmemory          2gb
maxmemory-policy   allkeys-lru
```

| Policy             | Behavior                                |
|--------------------|-----------------------------------------|
| `noeviction`       | Refuse writes when full. Safe for "DB". |
| `allkeys-lru`      | Drop least-recently-used keys.          |
| `allkeys-lfu`      | Drop least-frequently-used keys.        |
| `volatile-lru`     | LRU but only among keys with TTL.       |
| `volatile-ttl`     | Evict closest to expiry first.          |
| `allkeys-random`   | Random.                                 |

For a cache, **allkeys-lru** (or LFU) is the right default. For a primary store, **noeviction** — get alerted on memory pressure and scale up.

## Don't cache everything

A cache that's useful 5% of the time and adds 100% complexity is a net loss. Profile first. Cache the few endpoints whose latency dominates.
