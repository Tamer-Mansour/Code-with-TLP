# LRU Cache Simulator

An LRU (Least Recently Used) cache evicts the key that was accessed least recently when the cache is full. Both reads and writes count as accesses and update recency.

This exercise puts the eviction logic you learned about — `allkeys-lru` — into practice by building the data structure from scratch.

## What you will build

A cache that accepts two commands:

- `SET key value` — insert or update a key. If the cache is full, evict the least recently used key first.
- `GET key` — read a key and print its value, or `MISS` if the key is not in the cache.

Both `GET` and `SET` update the key's recency position.

## Input format

```
N
<command 1>
<command 2>
...
```

The first line is the cache capacity `N` (1 ≤ N ≤ 1000). Each subsequent line is either `SET key value` or `GET key`.

## Output format

Print one line for every `GET` command: the value if found, or `MISS`. `SET` commands produce no output.

## Example

```
Input:
3
SET a 1
SET b 2
SET c 3
GET a
SET d 4
GET b
GET a
GET d

Output:
1
MISS
1
4
```

Walkthrough:
1. Cache: `{a:1, b:2, c:3}` (oldest → newest: a, b, c)
2. `GET a` → hits, moves `a` to most-recent. Output: `1`
3. `SET d 4` → cache full, evict LRU which is now `b`. Cache: `{a:1, c:3, d:4}`
4. `GET b` → evicted. Output: `MISS`
5. `GET a` → hits. Output: `1`
6. `GET d` → hits. Output: `4`

## Constraints

- 1 ≤ N ≤ 1000
- Keys and values are non-empty alphanumeric strings
- Up to 10,000 commands
