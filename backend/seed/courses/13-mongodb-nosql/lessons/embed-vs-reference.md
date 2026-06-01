# Embed vs Reference

The big design choice in document modeling. There's no universal rule — only trade-offs.

## Embed

Nest related data inside the parent document.

```jsonc
{
  "_id": "ord_001",
  "customer": { "id": "u_42", "name": "Alice" },
  "items": [
    { "sku": "A", "qty": 2, "price": 9.99 },
    { "sku": "B", "qty": 1, "price": 4.50 }
  ]
}
```

**Pros:**
- One read returns the whole entity.
- Updates are atomic across the nested fields.
- Locality — disk + cache friendly.

**Cons:**
- Duplicated data (Alice's name repeated in every order).
- Updates to the duplicated facts are expensive (touch every order).
- Documents grow unbounded if the child set grows without limit.

## Reference

Store a foreign key:

```jsonc
{ "_id": "ord_001", "customer": "u_42", "items": ["i_a","i_b"] }
{ "_id": "u_42", "name": "Alice" }
{ "_id": "i_a", "sku": "A", "qty": 2, "price": 9.99 }
```

Fetch related data with a second query, or `$lookup`.

**Pros:**
- One source of truth per fact.
- Documents stay small.
- Updates are cheap.

**Cons:**
- Multiple reads to assemble a full view.
- `$lookup` is slower than a SQL join.

## The decision matrix

| If...                                                | Lean toward... |
|------------------------------------------------------|----------------|
| Children are owned by the parent (order items)       | **Embed**      |
| Children are large or unbounded (comments, events)   | **Reference**  |
| You always read parent + children together           | **Embed**      |
| Children are shared between many parents (tags)      | **Reference**  |
| Children update often and parent rarely              | **Reference**  |
| Parent updates often and children rarely             | **Embed**      |
| You need cross-entity transactions                   | **Reference + transactions** |

## Common patterns

### Bucket pattern (for time-series)

Instead of one doc per event, group events per minute/hour:

```jsonc
{ "_id": "sensor_1_2025-06-01T10", "samples": [10, 11, 12, ...], "count": 60 }
```

Fewer documents, tighter indexes.

### Computed pattern

Cache an aggregate in the parent document:

```jsonc
{ "_id": "u_42", "orderCount": 17, "lifetimeValue": 1234.50 }
```

Update with `$inc` on each new order. Read in O(1).

### Subset pattern

Embed *the most recent* N children, reference the rest:

```jsonc
{ "_id": "post_001", "recentComments": [...latest 10...], "commentCount": 482 }
```

Renders the post page in one read; full comment list loaded on demand.

## Heuristic

Start by **embedding**. Switch to references when:
- The document hits 1 MB or so.
- The child collection clearly has its own lifecycle.
- You find yourself updating the duplicated copies often.

It's far easier to split later than to consolidate — schemas are flexible, so begin with the simpler shape.
