# Rate Limiting with Redis

Rate limiting protects APIs from abuse, ensures fair usage among tenants, and prevents accidental DDoS from buggy clients. Redis is the preferred store for rate limiters because atomic increment operations make it trivially easy to count requests with no race conditions.

## The fixed-window counter

The simplest approach: count requests in a fixed time bucket.

```python
import redis, time

r = redis.Redis()

def is_allowed(user_id: str, limit: int = 100, window_seconds: int = 60) -> bool:
    bucket = int(time.time() // window_seconds)
    key = f"rate:{user_id}:{bucket}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, window_seconds * 2)  # auto-cleanup
    return count <= limit
```

One `INCR` + one conditional `EXPIRE` per request. Very fast.

**Limitation**: a user can send `2 × limit` requests in a window boundary — `limit` requests at the end of window N and `limit` at the start of window N+1.

## The sliding-window log

Store each request's timestamp in a sorted set. On every request, prune old entries and count what remains.

```python
def is_allowed_sliding(user_id: str, limit: int = 100, window_ms: int = 60_000) -> bool:
    key = f"rate:log:{user_id}"
    now_ms = int(time.time() * 1000)
    cutoff = now_ms - window_ms

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, cutoff)       # remove old entries
    pipe.zadd(key, {str(now_ms): now_ms})        # add this request
    pipe.zcard(key)                              # count in window
    pipe.expire(key, window_ms // 1000 + 1)
    _, _, count, _ = pipe.execute()

    return count <= limit
```

The pipeline executes atomically (pipelining, not MULTI/EXEC, but close enough for rate limiting). This gives a true sliding window but uses more memory — each request is a sorted-set entry.

## Token bucket with Lua

For smooth traffic shaping (burst-friendly), the **token bucket** algorithm is best implemented as a Lua script to guarantee atomicity:

```lua
-- KEYS[1] = key, ARGV[1] = capacity, ARGV[2] = refill_rate (tokens/sec),
-- ARGV[3] = now (unix float), ARGV[4] = tokens_requested
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local last = tonumber(redis.call("HGET", key, "last") or now)
local tokens = tonumber(redis.call("HGET", key, "tokens") or capacity)

local elapsed = now - last
tokens = math.min(capacity, tokens + elapsed * rate)

if tokens >= requested then
    tokens = tokens - requested
    redis.call("HSET", key, "tokens", tokens, "last", now)
    redis.call("EXPIRE", key, math.ceil(capacity / rate) * 2)
    return 1   -- allowed
else
    redis.call("HSET", key, "tokens", tokens, "last", now)
    return 0   -- denied
end
```

```python
allow_script = r.register_script(LUA_SCRIPT)
allowed = allow_script(
    keys=[f"bucket:{user_id}"],
    args=[100, 10, time.time(), 1]
)
```

## Comparison

| Algorithm | Memory | Burst handling | Boundary spike |
|---|---|---|---|
| Fixed window | O(1) per user | Yes | Yes (2x spike) |
| Sliding window log | O(requests in window) | Exact | No |
| Token bucket (Lua) | O(1) per user | Configurable | No |

## Returning rate-limit headers

Always tell the client how close they are to the limit:

```python
headers = {
    "X-RateLimit-Limit": str(limit),
    "X-RateLimit-Remaining": str(max(0, limit - count)),
    "X-RateLimit-Reset": str(bucket * window_seconds + window_seconds),
    "Retry-After": str(window_seconds) if count > limit else None,
}
```

## Multi-tier limiting

Layer limits at different granularities to prevent both short bursts and sustained abuse:

```python
def check_all(user_id: str) -> bool:
    return (
        is_allowed(user_id, limit=10, window_seconds=1)    # 10/sec burst
        and is_allowed(user_id, limit=100, window_seconds=60)  # 100/min
        and is_allowed(user_id, limit=1000, window_seconds=3600) # 1000/hr
    )
```
