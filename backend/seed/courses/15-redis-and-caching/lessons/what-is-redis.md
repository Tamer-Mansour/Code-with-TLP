# What is Redis?

Redis (REmote DIctionary Server) is an **in-memory data store** that speaks dozens of data-structure operations natively. It's commonly described as "a Swiss-army knife of fast storage": cache, queue, lock service, rate limiter, leaderboard, pub/sub bus — same server, different keys.

## Speed comes from being in-memory

All data lives in RAM. Operations are O(1) or O(log n) typically. A single Redis node easily handles 100,000+ ops/sec on commodity hardware, with sub-millisecond latency.

The trade: dataset size is bounded by available RAM (or RAM × number of shards).

## Single-threaded by default

Commands execute one at a time on a single thread, so there's no locking complexity. Atomicity per command is free. Throughput is "good enough" because each command takes microseconds.

Modern Redis (≥ 6.0) uses extra threads for I/O, not command processing — keeping the simplicity while scaling network throughput.

## Use Redis for

- **Cache** in front of slow stores (SQL, third-party APIs).
- **Session store** — strings or hashes with TTL.
- **Rate limiting** — `INCR` + `EXPIRE`.
- **Leaderboards** — sorted sets.
- **Job queues** — lists (`LPUSH`/`BRPOP`) or streams (`XADD`/`XREADGROUP`).
- **Pub/sub** — `PUBLISH`/`SUBSCRIBE`.
- **Distributed locks** — `SET key value NX EX 30`.
- **Counters** at high write rates.

## When Redis is NOT the right answer

- Your data won't fit in RAM (and you can't reasonably shard).
- You need ACID transactions across many keys with rollback.
- You need rich ad-hoc queries (use Postgres/MongoDB).
- You need cross-region replication with low latency in both directions (Redis is master-driven).

## Persistence — yes, even in-memory

Redis can write data to disk via RDB snapshots or AOF (append-only file). You don't *have* to, but most production setups do — it's the difference between "blip after restart" and "lost all the data."

## A first session

```
$ redis-cli
127.0.0.1:6379> SET hello world
OK
127.0.0.1:6379> GET hello
"world"
127.0.0.1:6379> INCR counter
(integer) 1
127.0.0.1:6379> INCR counter
(integer) 2
127.0.0.1:6379> EXPIRE counter 60
(integer) 1
```

That's the whole rhythm: short, predictable commands; one trip per call; persistence in the background.
