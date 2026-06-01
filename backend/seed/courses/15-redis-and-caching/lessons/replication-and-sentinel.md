# Replication and Sentinel

Redis replication is **master → replica**, asynchronous, fast. Sentinel is a separate process that monitors replication and orchestrates failover.

## Replication

```
[ master ]  --writes-->  [ replica 1 ]
                      \-> [ replica 2 ]
```

A replica connects to the master, asks for everything (initial RDB dump), then streams the master's command log forever.

On the replica:

```
replicaof master.internal 6379
masterauth somepass
```

Or runtime:

```
> REPLICAOF master.internal 6379
> REPLICAOF NO ONE          # promote to standalone
```

`INFO replication` shows the topology and replication offset on each side.

### Read scaling

Replicas serve **reads** in `slave-read-only yes` mode (default). Route read-only traffic to them via your client library or a proxy. Writes always go to the master.

### Replication is async

A write that's `OK` on the master may not yet exist on a replica. If the master dies before propagation, that write is lost. For at-most-N-seconds durability, configure `min-replicas-to-write` and `min-replicas-max-lag`:

```
min-replicas-to-write 1
min-replicas-max-lag  10
```

Writes are refused if no replica has been in sync within 10 seconds.

### Diskless replication

The initial sync to a new replica can stream directly from memory:

```
repl-diskless-sync yes
```

Avoids writing an RDB file on the master.

## Sentinel — managed failover

Sentinel is a small Redis-mode process that:

- Monitors the master and replicas.
- Detects when the master is down.
- Elects a new master (raft-style) among Sentinels.
- Promotes a replica.
- Reconfigures the other replicas to point at the new master.
- Updates clients via pub/sub.

Run an odd number of Sentinels (usually 3 or 5) across different hosts.

### Config

```
# sentinel.conf
sentinel monitor cache 10.0.0.1 6379 2
sentinel down-after-milliseconds cache 5000
sentinel failover-timeout cache 60000
sentinel parallel-syncs cache 1
```

`2` is the quorum — how many Sentinels must agree before a failover is allowed.

### Clients

Modern Redis clients have **Sentinel mode** — give them the Sentinel addresses; they discover the current master and reconnect on failover:

```python
r = Redis(connection_pool=SentinelConnectionPool(
    service_name="cache",
    sentinel_manager=Sentinel([("s1", 26379), ("s2", 26379), ("s3", 26379)])
))
```

## When to use Sentinel vs Cluster

| Need                                | Choose       |
|-------------------------------------|--------------|
| HA for a single-shard Redis         | **Sentinel** |
| Horizontal scale across many shards | **Cluster**  |
| Both                                | Cluster (it has HA built-in) |

We cover Cluster in a later lesson.

## Don't run Sentinel as the data nodes

In production, Sentinels live on separate hosts from the Redis data nodes — otherwise a host outage takes down both the data and the Sentinel quorum.

## Managed services

ElastiCache, MemoryDB, Upstash, Memorystore — they bundle HA failover for you. You configure replicas; they manage the orchestration. Don't roll your own Sentinel cluster if a managed service fits.
