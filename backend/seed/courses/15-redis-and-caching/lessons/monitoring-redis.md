# Monitoring Redis in Production

A Redis instance that nobody watches is one outage away from taking down your application. Effective monitoring focuses on four areas: memory, latency, connections, and persistence lag.

## The `INFO` command

`INFO` is your starting point. It returns a multi-section snapshot of the server state.

```
127.0.0.1:6379> INFO memory
# Memory
used_memory:1024000
used_memory_human:1000.00K
used_memory_rss:2097152
maxmemory:2147483648
maxmemory_policy:allkeys-lru
mem_fragmentation_ratio:1.23
```

Run `INFO all` for everything, or `INFO <section>` for a subset: `server`, `clients`, `memory`, `stats`, `replication`, `cpu`, `keyspace`.

## Key metrics to alert on

| Metric | Location | Alert threshold |
|---|---|---|
| `used_memory` | `INFO memory` | > 75% of `maxmemory` |
| `mem_fragmentation_ratio` | `INFO memory` | > 1.5 or < 1.0 |
| `connected_clients` | `INFO clients` | > 500 (tune to your pool size) |
| `blocked_clients` | `INFO clients` | > 0 sustained |
| `keyspace_hits` / `keyspace_misses` | `INFO stats` | miss rate > 20% is worth investigating |
| `rdb_last_bgsave_status` | `INFO persistence` | `err` = alert immediately |
| `aof_last_write_status` | `INFO persistence` | `err` = alert immediately |
| `master_last_io_seconds_ago` | `INFO replication` | > 30 s on a replica |

## `MONITOR` — use sparingly

```
127.0.0.1:6379> MONITOR
+1700000001.123456 [0 127.0.0.1:51234] "GET" "user:42"
+1700000001.124001 [0 127.0.0.1:51234] "SET" "counter" "7"
```

`MONITOR` streams every command in real time. It is invaluable for debugging but **halves throughput** on a busy instance — use it only in development or for short bursts in staging.

## Slow query log

Redis logs commands that exceed a configurable threshold:

```
# In redis.conf
slowlog-log-slower-than 10000   # microseconds (10 ms)
slowlog-max-len        128

# At runtime
CONFIG SET slowlog-log-slower-than 10000
SLOWLOG GET 10
```

Each entry shows: ID, timestamp, execution time in µs, and the exact command. Review this before blaming the database.

## `LATENCY` monitoring

```
127.0.0.1:6379> LATENCY LATEST
1) 1) "command"
   2) (integer) 1700000001
   3) (integer) 135       <- latest latency in ms
   4) (integer) 200       <- max latency in ms

127.0.0.1:6379> LATENCY HISTORY command
```

Enable latency monitoring in `redis.conf`:

```
latency-monitor-threshold 50  # ms, 0 = disabled
latency-tracking yes
```

## Prometheus + Grafana setup

The community **redis_exporter** (github.com/oliver006/redis_exporter) scrapes `INFO` and exposes Prometheus metrics. A ready-made Grafana dashboard (ID 763) gives you all the charts above in minutes.

```yaml
# docker-compose.yml snippet
redis_exporter:
  image: oliver006/redis_exporter
  environment:
    REDIS_ADDR: redis:6379
  ports:
    - "9121:9121"
```

## Memory fragmentation

A `mem_fragmentation_ratio` above 1.5 means Redis allocated memory from the OS but is using only a fraction of it. This typically happens after many key deletions. Fix:

```
127.0.0.1:6379> MEMORY PURGE
```

Or set `activedefrag yes` in `redis.conf` for continuous background defragmentation (Redis ≥ 4.0).

## Keyspace notifications

Enable notifications so your application can react to events (key expiry, set operations, etc.):

```
CONFIG SET notify-keyspace-events "KEA"
# K = keyspace, E = keyevent, A = all commands
```

Subscribe with `PSUBSCRIBE __keyevent@0__:expired` to react to every key expiry in database 0.
