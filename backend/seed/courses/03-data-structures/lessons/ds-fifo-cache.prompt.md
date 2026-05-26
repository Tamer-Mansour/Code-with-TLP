# FIFO Cache Simulator

Simulate a **FIFO cache** of capacity C. The cache maps integer keys to integer values.

Supported operations:

- `GET x` — if key x is in the cache, print its value. Otherwise print `MISS`.
  Getting a key does **not** change its eviction order (pure FIFO, not LRU).
- `PUT x y` — store key x with value y.
  - If key x is already in the cache, update its value. Do **not** change its eviction order.
  - If the cache is full (size == C) and x is a new key, evict the key that was inserted **earliest** (FIFO order), then insert x.
  - Print nothing for PUT.

## Input Format

```
C Q
op1
op2
...
```

- Line 1: integers C (cache capacity, 1 ≤ C ≤ 1000) and Q (number of operations, 1 ≤ Q ≤ 10000).
- Lines 2..Q+1: one operation per line. `GET x` or `PUT x y`.

## Output Format

For each `GET` operation, print the cached value or `MISS` on its own line.

## Example

Input:
```
2 9
PUT 1 10
PUT 2 20
GET 1
PUT 3 30
GET 1
GET 2
GET 3
PUT 2 99
GET 2
```

Output:
```
10
MISS
20
30
99
```

Explanation:
- After `PUT 1 10`, `PUT 2 20`: cache = {1:10, 2:20}, insertion order [1, 2].
- `GET 1` → 10.
- `PUT 3 30`: cache full, evict oldest (key 1). Cache = {2:20, 3:30}, order [2, 3].
- `GET 1` → MISS (evicted).
- `GET 2` → 20.
- `GET 3` → 30.
- `PUT 2 99`: key 2 already in cache, update value. Cache = {2:99, 3:30}. Order unchanged [2, 3].
- `GET 2` → 99.
