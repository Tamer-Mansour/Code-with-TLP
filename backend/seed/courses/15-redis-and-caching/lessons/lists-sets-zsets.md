# Lists, Sets, and Sorted Sets

Three collection types that solve very different problems.

## Lists (linked lists)

Ordered, allow duplicates, fast pushes/pops at both ends.

```
LPUSH q "job1"           # push to head
LPUSH q "job2" "job3"
RPUSH q "job4"           # push to tail

LRANGE q 0 -1            # all elements
LLEN   q

RPOP  q                  # pop tail
LPOP  q                  # pop head
```

### Blocking pops — queue primitive

```
BRPOP q 5                # wait up to 5s for an element on q
BLMOVE q q-processing LEFT RIGHT 5    # reliable handoff
```

Combined with a worker process this is a job queue. For more ceremony (consumer groups, ack, replays) use **Streams** instead.

### As a capped log

```
LPUSH recent "msg"
LTRIM recent 0 99       # keep newest 100 only
```

Constant memory, no expiry needed.

## Sets

Unordered collections of unique strings.

```
SADD   tags "redis" "cache"
SMEMBERS tags
SISMEMBER tags "redis"   -> 1
SCARD  tags              # cardinality
SREM   tags "cache"

SINTER tags1 tags2       # intersection
SUNION tags1 tags2
SDIFF  tags1 tags2
SRANDMEMBER tags 3       # 3 random
```

Use for: tags, deduplication, "who's online" sets, audience overlap analytics.

### HyperLogLog — sets at extreme scale

If you only need *approximate* cardinality of millions of items in ~12 KB total:

```
PFADD visitors:2025-06-01 "userA"
PFADD visitors:2025-06-01 "userB" "userC"
PFCOUNT visitors:2025-06-01
PFMERGE month visitors:2025-06-01 visitors:2025-06-02 ...
```

~0.81% error, constant memory. Magic for analytics dashboards.

## Sorted Sets (ZSETs)

Unique members, each with a floating-point **score**. The members are kept sorted by score, ties broken alphabetically.

```
ZADD board 100 "alice"
ZADD board 90  "bob"
ZADD board 95  "carol"

ZRANGE  board 0 -1 WITHSCORES                # ascending
ZREVRANGE board 0 2 WITHSCORES               # top 3 descending
ZRANGEBYSCORE board 80 (100                  # 80 ≤ score < 100
ZRANK board "carol"
ZSCORE board "alice"
ZINCRBY board 5 "alice"                      # +5 to alice's score
ZREM board "bob"
```

### Why ZSETs are special

Almost every "ranking" or "time-ordered" pattern works:

- **Leaderboard** — score = points, member = userID.
- **Time-ordered feed** — score = timestamp, member = postID.
- **Rate limiter (sliding window)** — score = timestamp, member = request ID; trim with `ZREMRANGEBYSCORE`.
- **Priority queue** — score = priority, `ZPOPMIN` to dequeue.
- **Schedulers** — score = run-at timestamp, poll with `ZRANGEBYSCORE 0 now`.

### Pop variants

```
ZPOPMIN board
ZPOPMAX board
BZPOPMIN board 5      # blocking
```

### Range by lex

For sorted-set members with the *same score*, you can range by string:

```
ZADD names 0 "alice" 0 "bob" 0 "carol"
ZRANGEBYLEX names "[a" "[c"
```

## Memory cost

Sorted sets are pricier than regular sets — extra structures for the order. For tens of millions of members consider sharding or HyperLogLog where appropriate.

## What to use when

| You need...                     | Use         |
|----------------------------------|-------------|
| Ordered queue / log              | List        |
| Unique membership                | Set         |
| Approximate count of huge set    | HyperLogLog |
| Ranked / time-ordered collection | Sorted Set  |
| Whole-object updates             | Hash        |
| Atomic counter                   | String      |
