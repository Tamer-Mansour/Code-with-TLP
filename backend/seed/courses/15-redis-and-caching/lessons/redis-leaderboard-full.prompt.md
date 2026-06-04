# Sorted Set Leaderboard

Simulate Redis Sorted Set operations for a leaderboard.

## Input

Commands one per line until EOF. No leading count.

## Commands

- `ZADD score member` — add or update `member` with the given numeric `score`
- `ZRANK member` — print the 0-based rank of `member` from lowest score; print `-1` if not found
- `ZREVRANK member` — print the 0-based rank from highest score; print `-1` if not found
- `ZRANGE start stop` — print members ranked `start` through `stop` inclusive (lowest to highest)
- `ZSCORE member` — print the score of `member`, or `NIL` if not found

Ties in score are broken alphabetically (ascending).

## Output

One line per `ZRANK`, `ZREVRANK`, or `ZSCORE` command. One line per member for `ZRANGE`. No output for `ZADD`.

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
