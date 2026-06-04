# Sorted Set Leaderboard (Full Redis Commands)

Redis Sorted Sets power some of the most popular backend features: leaderboards, real-time rankings, and time-ordered feeds. The key insight is that every member has a **floating-point score**, and Redis maintains members in sorted order at all times.

In this exercise you simulate the full set of Sorted Set query commands — the same ones the Redis server executes internally.

## Commands to implement

| Command | Description |
|---|---|
| `ZADD score member` | Add or update a member with the given score |
| `ZRANK member` | 0-based rank from lowest score (0 = lowest). Print `-1` if not found |
| `ZREVRANK member` | 0-based rank from highest score (0 = highest). Print `-1` if not found |
| `ZRANGE start stop` | Print members from rank `start` to `stop` inclusive (lowest to highest) |
| `ZSCORE member` | Print the score, or `NIL` if member does not exist |

**Tie-breaking rule**: when two members have the same score, rank them alphabetically (ascending).

## Input format

Commands arrive one per line, until EOF. No leading count line.

## Output format

Each `ZRANK`, `ZREVRANK`, `ZSCORE` command prints one line. `ZRANGE start stop` prints one line per member in the range. `ZADD` produces no output.

## Example

Input:
```
ZADD 100 alice
ZADD 200 bob
ZADD 150 carol
ZRANK alice
ZRANK bob
ZREVRANK alice
ZRANGE 0 2
ZSCORE carol
ZSCORE eve
```

Output:
```
0
2
2
alice
carol
bob
150
NIL
```

Explanation:
- Members sorted ascending: alice(100), carol(150), bob(200)
- `ZRANK alice` = 0 (lowest score)
- `ZRANK bob` = 2 (highest score, index 2)
- `ZREVRANK alice` = 2 (furthest from top)
- `ZRANGE 0 2` = all three members lowest-first
- `ZSCORE carol` = 150
- `ZSCORE eve` = NIL (not in set)

## Further reading

- [Database Caching Strategies Using Redis (AWS Whitepaper)](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/database-caching-strategies-using-redis.pdf) — section on Sorted Sets for ranking workloads
