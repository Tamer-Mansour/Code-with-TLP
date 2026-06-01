# Stampedes and Distributed Locks

Two problems Redis is unusually good at solving — *if* you avoid the classic mistakes.

## The thundering-herd / cache stampede

A key expires. A hundred requests arrive simultaneously, all miss, all hit the slow backend, all overwrite the same Redis key. Brief catastrophe.

### Mitigations

**1. Randomized TTLs.** Don't expire all related keys at the same wall-clock moment.

```python
ttl = base_ttl + random.randint(0, base_ttl // 10)
```

**2. Probabilistic early refresh.** Inspired by Memcached's "lease" idea: refresh *before* expiry with rising probability.

```python
def get_with_xfetch(key, ttl, beta=1.0):
    value, remaining, recompute_cost = redis_get_with_meta(key)
    if value is None or random.random() < math.exp(-beta * recompute_cost / remaining):
        value = recompute()
        redis.set(key, value, ex=ttl)
    return value
```

A reader near the expiry has a small chance to refresh, smoothing the burst.

**3. A short-TTL "lock" key — single-flight.**

```python
def get_user(uid):
    v = redis.get(key)
    if v is not None: return v

    got_lock = redis.set(f"lock:{key}", "1", nx=True, ex=10)
    if got_lock:
        v = compute_user(uid)
        redis.set(key, v, ex=300)
        redis.delete(f"lock:{key}")
        return v
    else:
        # wait briefly and re-read
        time.sleep(0.05)
        return redis.get(key) or compute_user(uid)
}
```

Only one process recomputes; everyone else sees the new value moments later.

## Distributed locks

Redis can act as a mutex across processes. The minimal correct pattern:

```python
def acquire(lock_key, token, ttl_ms):
    return redis.set(lock_key, token, nx=True, px=ttl_ms)

# unlock atomically (only release if we still hold it)
unlock_lua = """
if redis.call('get', KEYS[1]) == ARGV[1] then
  return redis.call('del', KEYS[1])
else
  return 0
end
"""
def release(lock_key, token):
    redis.eval(unlock_lua, 1, lock_key, token)
```

- `NX` ensures the lock is acquired only if not already held.
- `PX` sets a TTL — a crashed holder can't deadlock the system forever.
- `token` is a unique random value. Releasing checks the value so you don't release someone else's lock if your TTL expired and they re-acquired.

### Pitfalls

- **TTL too short** — your worker crosses the TTL mid-operation; another worker starts; you both write. Use a TTL longer than the worst-case operation duration **and renew it** in long jobs.
- **No fencing token** — if your TTL expires and you keep writing, the new holder + you both modify state. For correctness, hand a monotonically increasing **fence token** to the protected resource and have it reject stale tokens.

### Redlock — multi-master

For HA Redis setups, Martin Kleppmann's critique of Redlock is worth reading. The short version: a single-Redis distributed lock is *fine for mutual exclusion under normal failures*. For strict correctness in adversarial conditions, use Zookeeper / etcd / Consul.

## Idempotency

Caches *will* serve stale data; locks *will* sometimes be held twice. Design downstream operations to be **idempotent** wherever possible — repeating them produces the same result. It's the right defensive posture for any distributed system, Redis or not.
