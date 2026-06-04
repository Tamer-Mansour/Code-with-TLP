# Cache Hit Rate Analyzer

Simulate the cache-aside (lazy loading) pattern and compute the cache hit rate.

## Input

```
N
TTL
READ key1
READ key2
...
```

- Line 1: cache capacity `N`
- Line 2: TTL in number of operations (a cached entry expires after this many operations have elapsed since it was inserted)
- Remaining lines: `READ key` commands

## Rules

- On `READ key`:
  - If the key is in the cache and has not expired, it is a **HIT** — print `HIT: <value>`.
  - Otherwise it is a **MISS** — fetch value as `key + "_val"`, store in cache, print `MISS: <value>`.
- A key expires when `(current_op - insert_op) >= TTL`.
- When the cache is at capacity and a new key must be inserted, evict the **oldest inserted key** (FIFO).
- Each `READ` counts as one operation (starting at op 1).

## Output

For each `READ` command, print `HIT: <value>` or `MISS: <value>`.

After all reads, print one summary line:

```
Total: X, Hits: Y, Misses: Z, Hit Rate: P%
```

where `P` is the hit rate as a percentage rounded to 1 decimal place.

## Example

Input:
```
2
3
READ user:1
READ user:2
READ user:1
READ user:3
READ user:1
READ user:2
```

Output:
```
MISS: user:1_val
MISS: user:2_val
HIT: user:1_val
MISS: user:3_val
MISS: user:1_val
MISS: user:2_val
Total: 6, Hits: 1, Misses: 5, Hit Rate: 16.7%
```

## Constraints

- 1 ≤ N ≤ 100
- 1 ≤ TTL ≤ 1000
- Up to 1000 READ commands
