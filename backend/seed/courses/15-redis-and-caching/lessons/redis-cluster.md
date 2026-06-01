# Redis Cluster Sharding

When one Redis can't hold all your keys, **Cluster** shards them across many nodes. Cluster is built into Redis since 3.0 — no proxy required.

## Hash slots

Cluster doesn't shard by node count; it shards by **16384 hash slots**. Each key's slot is `CRC16(key) mod 16384`. Each master owns a range of slots.

```
master A: slots 0      - 5499
master B: slots 5500   - 10999
master C: slots 11000  - 16383
```

When you rebalance, you move slots — not individual keys — between masters.

## Topology

A cluster is a set of master/replica pairs (or triplets). Each shard has one master plus N replicas, and the masters together cover all 16384 slots.

```
Shard 1: A (master)  ← rep A1, A2
Shard 2: B (master)  ← rep B1, B2
Shard 3: C (master)  ← rep C1, C2
```

Minimum production cluster: 3 masters + 3 replicas across 3+ hosts (so one host failing doesn't take a shard's master *and* replica).

## Setting up a cluster

The friendly way:

```
redis-cli --cluster create \
  10.0.0.1:6379 10.0.0.2:6379 10.0.0.3:6379 \
  10.0.0.4:6379 10.0.0.5:6379 10.0.0.6:6379 \
  --cluster-replicas 1
```

Now any node can be a client entry point.

## Client-side awareness

Cluster-mode clients fetch the **slot map** on connect and route each command to the right node. If you talk to the wrong node:

```
(error) MOVED 12182 10.0.0.3:6379
```

Smart clients update the map and follow the redirect transparently.

## Multi-key operations

A single command must reference keys that **all live in the same slot** — otherwise:

```
(error) CROSSSLOT Keys in request don't hash to the same slot
```

This breaks transactions, Lua scripts, and `MSET` across shards.

### Hash tags

Force two keys into the same slot by sharing a `{tag}`:

```
user:{42}:profile
user:{42}:orders
```

Both hash on `42` only, landing in the same slot. Use sparingly — over-tagging unbalances the cluster.

## Resharding

Move slots without downtime:

```
redis-cli --cluster reshard 10.0.0.1:6379
```

You'll be asked: how many slots, from which source nodes, to which destination. Cluster handles the live migration with `MIGRATE` commands; clients see brief `ASK` redirects mid-move.

## Failover

If a master dies, its replicas vote one of themselves to take over. Typically ~10 seconds.

`min-replicas-to-write` works in Cluster too — write to a master only if at least N replicas are in sync.

## Cluster vs Sentinel

| Need                       | Use      |
|----------------------------|----------|
| HA, one shard's worth      | Sentinel |
| Many shards + HA           | Cluster  |
| Online resharding          | Cluster  |
| Simpler client library     | Sentinel |

## Limits to remember

- **No multi-key commands across slots.** Plan keys.
- **Pub/Sub** in Cluster is propagated to all nodes — fine for small message volumes, inefficient for high volume.
- **Lua scripts** must touch only keys in one slot.
- **Some clients** still lack mature Cluster support — check before adopting.

## Managed equivalents

Amazon ElastiCache (cluster mode), Azure Cache for Redis (cluster), Google Memorystore, Upstash, Redis Cloud. Same Cluster underneath; they hide ops.
