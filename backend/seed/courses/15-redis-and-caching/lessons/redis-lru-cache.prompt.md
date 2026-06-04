# LRU Cache Simulator

Implement an LRU (Least Recently Used) cache with a fixed capacity.

## Input

```
N
<command 1>
<command 2>
...
```

The first line is the cache capacity `N`. Each subsequent line is one of:

- `SET key value` — add or update the key. If inserting a new key and the cache is already at capacity, evict the least recently used key first.
- `GET key` — retrieve the value for the key. Both GET and SET update the key's recency.

## Output

Print one line per `GET`:
- The value if the key is present in the cache.
- `MISS` if the key is not present.

`SET` commands produce no output.

## Example

Input:
```
3
SET a 1
SET b 2
SET c 3
GET a
SET d 4
GET b
GET a
GET d
```

Output:
```
1
MISS
1
4
```

## Constraints

- 1 ≤ N ≤ 1000
- Keys and values are non-empty alphanumeric strings
- Up to 10,000 commands total
