# Indexes, Compound Indexes, and ESR

MongoDB uses **B-tree** indexes — same idea as SQL databases. Every collection automatically has an index on `_id`. Add more for query speed.

## Creating indexes

```javascript
db.users.createIndex({ email: 1 }, { unique: true });
db.orders.createIndex({ customer: 1, createdAt: -1 });
```

`1` is ascending, `-1` is descending. For single-field indexes the direction rarely matters; for compound indexes (and sorts) it absolutely does.

## Listing and dropping

```javascript
db.orders.getIndexes();
db.orders.dropIndex("customer_1_createdAt_-1");
```

## Compound indexes and prefixes

```javascript
db.orders.createIndex({ status: 1, customer: 1, createdAt: -1 });
```

This index can serve queries that filter on:

- `status` alone ✓
- `status` + `customer` ✓
- `status` + `customer` + `createdAt` ✓ (perfect)
- `customer` alone ✗ (no `status` prefix)
- `createdAt` alone ✗

**Leftmost-prefix rule**: an index serves a query whose filtered/sorted fields form a *prefix* of the index keys.

## The ESR rule

When building compound indexes, order your fields:

- **E**quality first
- **S**ort second
- **R**ange last

Example: query is

```javascript
db.orders.find({ status: "paid", createdAt: { $gte: D } })
         .sort({ amount: -1 });
```

Equality on `status`, sort on `amount`, range on `createdAt`. Build:

```javascript
db.orders.createIndex({ status: 1, amount: -1, createdAt: 1 });
```

ESR ordering lets MongoDB walk the index in the order you want — no separate sort step, no scanning past extra rows.

## Index types beyond standard

- **Unique** — duplicate values rejected.
- **Sparse** — index only documents that have the field.
- **TTL** — expire documents after a duration.
  ```javascript
  db.sessions.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });
  ```
- **Text** — for `$text` full-text search.
- **2dsphere** — for GeoJSON queries (`$near`, `$geoWithin`).
- **Hashed** — supports hashed sharding; no range queries.
- **Wildcard** — index across many varying fields:
  ```javascript
  db.metadata.createIndex({ "$**": 1 });
  ```

## Covered queries

If the query and projection together only need fields in the index, MongoDB doesn't read documents at all:

```javascript
db.users.createIndex({ email: 1, isActive: 1 });
db.users.find({ email: "a@b.com" }, { email: 1, isActive: 1, _id: 0 });
```

`explain()` shows `IXSCAN` with no `FETCH` stage — that's a covered query. Fast.

## Cost of indexes

Every index slows down writes (a little) and uses RAM. Index your hot query patterns; don't index hopefully.

## Background and concurrent index builds

In modern MongoDB, index builds are concurrent by default — they don't block writes. Still expensive on huge collections; schedule for off-peak.
