# Index Selectivity Analyzer

Choosing which fields to index is one of the most impactful performance decisions in MongoDB. The key concept is **selectivity** — an index is useful only if it narrows down the candidate documents significantly.

## The Exercise

Given N field values (one per line), compute the **selectivity** of an index on that field:

```
selectivity = unique_values / total_values
```

Classify the result as:

- `HIGH` — selectivity >= 0.8 (index will be very effective)
- `MEDIUM` — selectivity >= 0.5 (index moderately useful)
- `LOW` — selectivity < 0.5 (index likely not worth it)

Output format: `selectivity:<ratio> quality:<LEVEL>` where ratio is rounded to 2 decimal places.

## Why Selectivity Matters

Consider an index on a `status` field with values `active` or `inactive`. If 95% of documents are `active`, filtering `{ status: "active" }` still examines 95% of the collection — the index barely helps. MongoDB's query planner may skip the index entirely.

Contrast with an index on `email` where every value is unique. Selectivity = 1.0. MongoDB can jump directly to the matching document.

```javascript
// Low-selectivity field — index rarely useful
db.users.createIndex({ status: 1 });  // "active"|"inactive"|"suspended"

// High-selectivity field — index very useful
db.users.createIndex({ email: 1 }, { unique: true });
db.orders.createIndex({ orderId: 1 }, { unique: true });
```

## How MongoDB's Query Planner Uses Selectivity

When MongoDB evaluates a query plan, it estimates how many documents each candidate index will scan. This estimate is based on:

1. **Index cardinality** — how many distinct values exist.
2. **Value frequency distribution** — even spread vs. heavy skew.

You can inspect this with `explain("executionStats")`:

```javascript
db.orders.find({ status: "paid" }).explain("executionStats");
// Look at: totalKeysExamined vs nReturned
// Ratio close to 1.0 = high selectivity, index is doing work
// Ratio of 100:1 = index examines 100 docs to return 1 = low selectivity
```

## Real Examples

| Field | Typical Selectivity | Notes |
|-------|---------------------|-------|
| `_id` (ObjectId) | 1.0 | Always unique |
| `email` | ~1.0 | Should be unique |
| `country` | 0.01 – 0.05 | ~200 countries, millions of users |
| `status` | 0.01 – 0.10 | 3–5 values for millions of docs |
| `createdAt` (timestamp) | ~1.0 | Practically unique |
| `category` | 0.10 – 0.50 | Depends on catalog size |

## Anti-Pattern: Indexing Low-Cardinality Fields Alone

Indexing `{ isActive: 1 }` on a boolean field is usually wasteful — two possible values means 50% selectivity at best. This type of index consumes RAM and slows writes without meaningfully speeding reads.

**Better:** Combine with a high-selectivity field in a compound index:

```javascript
// Rarely useful alone:
db.users.createIndex({ isActive: 1 });

// Useful as part of a compound index:
db.users.createIndex({ isActive: 1, createdAt: -1 });
// Queries filtered on isActive AND sorted by createdAt become very fast
```

## TTL Indexes and Selectivity

TTL indexes (for auto-expiring documents) must be on a `Date` field. Because timestamps are highly selective, TTL indexes also work well as query indexes:

```javascript
db.sessions.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });
// Also serves: db.sessions.find({ expiresAt: { $gt: now } })
```

## Further Reading

- Christof Strauch, *NoSQL Databases* (HDM Stuttgart), §5.4 — Indexing strategies in document stores: [https://www.christof-strauch.de/nosqldbs.pdf](https://www.christof-strauch.de/nosqldbs.pdf)
- MongoDB documentation: *Indexing Strategies* — Index Selectivity and Cardinality.
