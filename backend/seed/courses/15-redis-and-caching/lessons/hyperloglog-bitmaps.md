# HyperLogLog and Bitmaps

Redis ships two compact data structures that solve cardinality counting and per-user boolean tracking with dramatically less memory than naive approaches.

## HyperLogLog

`HyperLogLog` (HLL) is a **probabilistic data structure** for counting distinct elements. It does not store elements themselves — it estimates how many unique items have been added. The estimate has at most a 0.81% standard error and uses a constant 12 KB of memory regardless of the number of distinct elements tracked.

### Commands

| Command | Description |
|---|---|
| `PFADD key el1 el2 …` | Add elements to the HLL |
| `PFCOUNT key [key …]` | Estimate cardinality (distinct count) |
| `PFMERGE dest src [src …]` | Merge multiple HLLs into one |

### Typical use cases

- **Unique visitor counts** per page, per day — without storing every user ID.
- **Unique search terms** seen in a time window.
- **AB-test** reach tracking.

```
127.0.0.1:6379> PFADD uv:2024-01-01 user:1 user:2 user:3 user:2
(integer) 1
127.0.0.1:6379> PFCOUNT uv:2024-01-01
(integer) 3
127.0.0.1:6379> PFADD uv:2024-01-02 user:3 user:4 user:5
(integer) 1
127.0.0.1:6379> PFMERGE uv:week uv:2024-01-01 uv:2024-01-02
OK
127.0.0.1:6379> PFCOUNT uv:week
(integer) 5
```

Memory comparison: storing 1 million user IDs as a Redis set would cost ~50 MB; HLL costs 12 KB — a 4000x reduction.

**Trade-off**: You get an approximate count, not an exact one, and you cannot iterate over or retrieve the elements.

## Bitmaps

A Redis `Bitmap` is not a distinct type — it is a **string** accessed via bit-level commands. Each bit in the string is individually addressable by offset. You can represent 1 billion boolean flags in 128 MB.

### Commands

| Command | Description |
|---|---|
| `SETBIT key offset 0\|1` | Set a single bit |
| `GETBIT key offset` | Read a single bit |
| `BITCOUNT key [start end]` | Count bits set to 1 |
| `BITOP AND\|OR\|XOR\|NOT dest key [key …]` | Bitwise operations across keys |
| `BITPOS key 0\|1 [start [end]]` | Find first set or clear bit |

### Worked example: Daily user activity

Track which users logged in on a given day. The offset is the user ID.

```
# User 42 and user 100 logged in on 2024-01-01
SETBIT logins:2024-01-01 42 1
SETBIT logins:2024-01-01 100 1

# How many users logged in?
BITCOUNT logins:2024-01-01
# -> 2

# Did user 42 log in?
GETBIT logins:2024-01-01 42
# -> 1

# Which users logged in on BOTH Jan 1 and Jan 2?
BITOP AND active:both logins:2024-01-01 logins:2024-01-02
BITCOUNT active:both
```

A key holding 1 million user flags costs only 125 KB — vastly cheaper than a Redis set.

## Choosing between HLL and Bitmap

| Need | Use |
|---|---|
| Approximate count of unique items | HyperLogLog |
| Exact count of which specific users did X | Bitmap |
| Bitwise intersection / union of user sets | Bitmap + `BITOP` |
| Memory budget is extremely tight | HyperLogLog |

Both structures shine in analytics workloads where you care about aggregate behavior rather than individual records.
