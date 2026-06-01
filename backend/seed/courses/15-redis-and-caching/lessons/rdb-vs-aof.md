# RDB vs AOF Persistence

Redis is in-memory, but it can persist to disk so a restart doesn't lose everything. There are two mechanisms; you can use either or both.

## RDB — point-in-time snapshots

A binary dump of the dataset. Written periodically by a child process via `fork()`:

```
save 900 1       # snapshot if at least 1 key changed in 900s
save 300 10
save 60  10000
dbfilename "dump.rdb"
dir "/var/lib/redis"
```

Trigger manually:

```
> BGSAVE
```

Pros:
- **Tiny on disk** — compact binary.
- **Fast restart** — load is a sequential read.
- **Backup-friendly** — one file you can `rsync` somewhere.

Cons:
- **Data loss window** — anything between snapshots is gone on crash.
- **Fork cost** — on a big dataset the COW fork pauses Redis briefly.

## AOF — append-only file

Every write command is appended to a log. On restart Redis replays it.

```
appendonly yes
appendfsync everysec     # fsync once per second (default)
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

`appendfsync` options:

| Setting    | Durability                          | Throughput cost                |
|------------|-------------------------------------|--------------------------------|
| `always`   | Every write fsynced                 | Slow                           |
| `everysec` | At most 1s of writes lost on crash  | Negligible (default)           |
| `no`       | OS decides when to fsync            | Fast but unpredictable loss    |

### AOF rewrite

The AOF grows forever. Periodically Redis **rewrites** it: a child process produces a new AOF representing the current state in the minimum number of commands. Configured via `auto-aof-rewrite-percentage` and `auto-aof-rewrite-min-size`.

Pros:
- **Stronger durability** — at most 1 second of data loss with `everysec`.
- **Human-readable** for emergency forensics.

Cons:
- **Bigger files** than RDB.
- **Slower restarts** (replay).

## Both

Redis 7+ uses a hybrid by default — the AOF starts with an RDB snapshot then appends. Best of both: fast restart + small data-loss window.

Enable with:

```
appendonly yes
aof-use-rdb-preamble yes
```

## What to choose

| You care about...               | Choose                                    |
|---------------------------------|-------------------------------------------|
| Pure cache; loss is acceptable  | RDB only (or disable persistence entirely)|
| Session/user data               | AOF `everysec`                            |
| Primary store                   | RDB + AOF, replication, regular backups   |

## Backups

`dump.rdb` is the backup target — copy it to S3 or wherever your other backups live. Treat as you would a database dump: tested restores, retention policy, off-site copy.

## When persistence is bad

If Redis is your cache and you can rebuild it from the primary store, persistence costs latency for no real gain. `save ""` disables RDB; `appendonly no` disables AOF. Document the choice — your future on-call will appreciate it.
