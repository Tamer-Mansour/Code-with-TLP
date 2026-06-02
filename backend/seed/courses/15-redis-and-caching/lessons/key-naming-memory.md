# Key Naming Conventions and Memory Optimization

How you name keys and structure values has a direct impact on memory consumption and operational sanity. These are not cosmetic choices.

## Key naming conventions

A consistent naming scheme turns `redis-cli --scan` and `KEYS` from a chaos dump into readable namespaces.

**Recommended pattern:** `<service>:<object>:<id>[:<field>]`

```
user:profile:42
user:session:abc123
order:items:99:total
rate:limit:api:user:42:2024-01-01
cache:product:1234
```

Rules of thumb:
- Use `:` as the namespace separator (it's the Redis convention; monitoring tools and redis-cli understand it).
- Keep keys short — every character costs memory multiplied by millions of keys.
- Never put a timestamp in the key body if a TTL can express time.
- Use a short prefix to group keys by service so you can `SCAN MATCH user:*` for targeted inspection.

## The `OBJECT ENCODING` command

Redis selects a compact internal encoding based on size:

```
127.0.0.1:6379> SET counter 1
OK
127.0.0.1:6379> OBJECT ENCODING counter
"int"

127.0.0.1:6379> SET message "hello world"
OK
127.0.0.1:6379> OBJECT ENCODING message
"embstr"    <- small strings stored inline in the robj header

127.0.0.1:6379> SET big "aaaaa....(>44 chars)..."
OK
127.0.0.1:6379> OBJECT ENCODING big
"raw"
```

Similarly for hashes:

| Encoding | Condition |
|---|---|
| `ziplist` / `listpack` | ≤ 128 fields AND every value ≤ 64 bytes |
| `hashtable` | > 128 fields OR any value > 64 bytes |

`ziplist`/`listpack` is a contiguous byte array — much more cache-friendly than a hash table. **Keep hashes small** to retain this encoding.

## Small-hash trick

Instead of one key per object field:

```
SET user:42:name "Alice"
SET user:42:email "alice@example.com"
SET user:42:score 9800
```

...use a single hash (stays in ziplist encoding when small):

```
HSET user:42 name Alice email alice@example.com score 9800
```

Memory reduction: ~60–80% for typical user objects because the per-key overhead (robj header, dict bucket, SDS string) is paid once, not per field.

## Compressing values

For large JSON blobs stored as strings, compress before storing:

```python
import zlib, json, redis

r = redis.Redis()
data = {"profile": "...", "history": [...]}    # large object
r.set("user:profile:42", zlib.compress(json.dumps(data).encode()))

raw = r.get("user:profile:42")
obj = json.loads(zlib.decompress(raw))
```

Compression typically achieves 60–80% size reduction on JSON. The CPU cost is negligible compared to the network and memory savings.

## `MEMORY USAGE`

Check the true memory cost of any key (includes the key string itself, value encoding overhead, and per-key metadata):

```
127.0.0.1:6379> MEMORY USAGE user:42
(integer) 184    <- bytes

127.0.0.1:6379> MEMORY USAGE product:9999 SAMPLES 5
(integer) 2048
```

Use `MEMORY DOCTOR` for a quick health report on the instance's memory state.

## Key eviction and TTL discipline

Memory optimization is not just structure — it's lifecycle:

- **Always set a TTL** on cache keys. A cache key without a TTL is a memory leak.
- Use `OBJECT IDLETIME key` to find keys that haven't been accessed recently.
- Audit with `redis-cli --bigkeys` to find the top memory consumers.

```bash
redis-cli --bigkeys
# Scans the whole keyspace, reports the largest key per type
```

Run `--bigkeys` during low-traffic hours; it uses `SCAN` internally (non-blocking) but still adds load.
