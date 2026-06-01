# Replica Sets and Failover

A **replica set** is a group of MongoDB nodes that hold copies of the same data. One node is the **primary** (accepts writes); the others are **secondaries** (replicate from the primary and can serve reads).

Production deployments **always** use replica sets — even if you only ever need one. They're how MongoDB does high availability.

## Topology

```
        Client
          │ writes
          ▼
       PRIMARY  ←─── oplog ───→  SECONDARY 1
          ▲                 ─→  SECONDARY 2
          │
       election if primary dies
```

A typical replica set has 3 or 5 voting members. Odd numbers help elections.

## The oplog

The **oplog** (operations log) is a capped collection on the primary that records every write. Secondaries tail it and replay each op. Same idea as MySQL binlog or PostgreSQL WAL.

```javascript
use local;
db.oplog.rs.find().sort({ $natural: -1 }).limit(5);
```

## Setup outline

```javascript
// On each node, start mongod with --replSet rs0
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "m1:27017" },
    { _id: 1, host: "m2:27017" },
    { _id: 2, host: "m3:27017" }
  ]
});
rs.status();
```

After a few seconds you have a working cluster.

## Read preferences

Tell the driver where to read:

| `readPreference`     | Meaning                                       |
|----------------------|-----------------------------------------------|
| `primary` (default)  | Reads from primary only — fully consistent.   |
| `primaryPreferred`   | Primary if available, else secondary.         |
| `secondary`          | Always read from a secondary.                 |
| `secondaryPreferred` | Secondary if available, else primary.         |
| `nearest`            | Lowest latency member, primary or secondary.  |

Secondary reads can be **stale** — milliseconds behind the primary on a healthy cluster, more under load.

## Write concern

Tells the primary *when* to acknowledge a write:

- `w: 1` — primary only (default). Fast, but a primary crash before replication = data loss.
- `w: "majority"` — wait until a majority of voting members has applied it. Safe; survives primary loss.
- `w: 3, j: true` — wait for 3 nodes including journal write to disk. Strongest.

```javascript
db.orders.insertOne(doc, { writeConcern: { w: "majority" } });
```

## Read concern

Pairs with write concern:

- `"local"` — current data on the node you talked to.
- `"majority"` — only data that has been replicated to a majority. Never returns rolled-back writes.

For mission-critical writes use **w: "majority"** + **readConcern: "majority"**.

## Failover

If the primary dies:

1. Surviving members notice the missed heartbeats.
2. An election runs (Raft-style protocol).
3. A secondary becomes the new primary, usually in ~10 seconds.
4. Drivers retry buffered writes automatically with retryable writes.

The application sees brief errors. Idempotent code paths recover transparently.

## Arbiters (avoid in production)

A voting member without data. Cheaper but reduces fault tolerance — if your data members crash, the arbiter alone can't serve reads. Use a **data-bearing odd number** instead.
