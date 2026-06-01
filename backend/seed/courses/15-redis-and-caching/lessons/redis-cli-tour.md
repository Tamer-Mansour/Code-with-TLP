# A Tour of redis-cli

`redis-cli` is the canonical Redis client. It's tiny, ubiquitous, and built for interactive exploration.

## Connect

```bash
redis-cli                              # localhost:6379, no auth
redis-cli -h cache.internal -p 6379
redis-cli -u redis://default:pass@host:6379/0
```

`-n N` selects a logical database (0–15 by default).

## The basics

```
> SET foo bar
OK
> GET foo
"bar"
> DEL foo
(integer) 1
> EXISTS foo
(integer) 0
```

Keys are strings. Values can be many types — but you decide at write time by which command you use (`SET`/`HSET`/`LPUSH`/`SADD`/`ZADD`).

## Inspecting keys

```
> KEYS *               (DON'T use in production — O(n))
> SCAN 0 MATCH user:*  (cursor-based, safe)
> TYPE mykey
> TTL mykey            (-1 no expiry, -2 doesn't exist)
> OBJECT ENCODING k    (internal storage hint)
```

`SCAN` is the production-safe way to iterate keys without blocking the server for huge keyspaces.

## TTL — let keys expire

```
> SET session:42 "..." EX 3600         # one hour
> EXPIRE session:42 600                # change to 10 minutes
> PERSIST session:42                   # remove expiry
> TTL session:42
(integer) 600
```

A huge fraction of Redis usage is "set, expire, forget."

## Pipelining

Send many commands without waiting for replies between them. Massive speedup for bursts:

```bash
echo -e "SET a 1\nSET b 2\nSET c 3" | redis-cli --pipe
```

In code, every Redis client supports pipelines. Use them whenever you have a known batch of commands — saves round trips.

## MONITOR — see every command live

```
> MONITOR
1717000000.123 [0 127.0.0.1:54321] "GET" "user:42"
1717000000.124 [0 127.0.0.1:54322] "SET" "session:88" "..."
```

Great for debugging in dev. **Never leave on in production** — it dramatically slows the server.

## INFO and SLOWLOG

```
> INFO server
> INFO memory
> INFO replication
> SLOWLOG GET 10            # 10 slowest recent commands
```

`INFO memory` is the first thing to look at when "Redis is slow / Redis got killed."

## CLIENT and KILL

```
> CLIENT LIST
> CLIENT KILL ID 12345
> CLIENT NO-EVICT on        # protect a client from eviction
```

Useful when a stale connection is hogging resources.

## CONFIG

```
> CONFIG GET maxmemory-policy
> CONFIG SET maxmemory-policy allkeys-lru
> CONFIG REWRITE             # persist runtime changes to the .conf file
```

Hot-reload tunable settings without restarts.

## Exiting

`exit`, `quit`, or Ctrl-D.

## A pro tip

`redis-cli --latency` shows live ping latency. `redis-cli --bigkeys` scans for unusually large keys (the #1 cause of latency spikes in poorly-modeled Redis setups). Run it monthly.
