# Sharding for Scale

When a single replica set runs out of RAM, CPU, or disk, MongoDB **shards** — distributes one collection across multiple replica sets. Each shard owns a subset of documents.

## The pieces

```
Application
   │
   ▼
mongos (router)  ←──── config servers (metadata about chunks)
   │
   ├──► Shard A (replica set)
   ├──► Shard B (replica set)
   └──► Shard C (replica set)
```

- **`mongos`** — a stateless query router. Clients connect to `mongos`, not directly to shards.
- **Config servers** — a small replica set storing the **shard map** (which range goes to which shard).
- **Shards** — full replica sets each holding part of the data.

## Shard keys

Each sharded collection has a **shard key**: one or more indexed fields that MongoDB hashes or ranges on.

```javascript
sh.shardCollection("shop.orders", { customer: "hashed" });
sh.shardCollection("shop.events", { tenant_id: 1, ts: 1 });
```

Two strategies:

- **Hashed** — value is hashed, distribution is even, no range scans across shards.
- **Range** — adjacent values land on the same shard, range queries can be targeted.

## Choosing a shard key

A bad shard key is the most common cause of MongoDB pain. A good shard key has:

1. **High cardinality** — many distinct values (millions+).
2. **Even write distribution** — no single value gets disproportionate writes.
3. **Targeted queries** — most reads filter on the shard key so `mongos` can route to one shard.
4. **Monotonic OK only if hashed** — a monotonically increasing key (like a timestamp) with range sharding creates a **hot shard**.

The first three are non-negotiable. **You cannot change a shard key easily.** Choose carefully or live with it.

## Targeted vs scatter-gather

- **Targeted query**: filter includes the shard key. `mongos` routes to one shard.
- **Scatter-gather**: no shard key filter. `mongos` queries every shard and merges. Expensive at scale.

Index your queries to be targeted whenever you can.

## Chunks and the balancer

The cluster splits each collection into **chunks** (default 64 MB). The **balancer** background process moves chunks between shards to keep them roughly even.

```javascript
sh.status();           // shards, chunk distribution, balancer state
sh.getBalancerState();
sh.startBalancer();
```

## Zones

Pin specific ranges to specific shards — e.g., GDPR data to EU-hosted shards:

```javascript
sh.addShardTag("shard0", "EU");
sh.addTagRange("shop.users",
  { country: "DE" }, { country: "DF" }, "EU");
```

## When to shard

The rough rules:

- Working set won't fit in RAM on a single replica set.
- Disk usage approaching limit.
- Write throughput saturates a single primary.

Sharding adds operational complexity. **Defer it** as long as your replica set can keep up — bigger machines and good indexes solve most problems.

## Atlas

If you're on MongoDB Atlas, sharding is a UI checkbox. You still pick the shard key. Pick well.
