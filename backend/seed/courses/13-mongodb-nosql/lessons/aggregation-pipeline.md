# The Aggregation Pipeline

The aggregation framework is MongoDB's answer to SQL's `GROUP BY`, `JOIN`, and analytical queries. You build a **pipeline** of stages, and documents flow through them like a Unix pipeline.

## Shape

```javascript
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $group: { _id: "$customer", total: { $sum: "$amount" } } },
  { $sort:  { total: -1 } },
  { $limit: 10 }
]);
```

Each stage takes documents in, transforms them, and passes them down. The stages above:

1. **`$match`** — filter (like `WHERE`). Always put `$match` and `$project` as early as possible to shrink the input.
2. **`$group`** — group by `_id`, compute aggregates.
3. **`$sort`** — order results.
4. **`$limit`** — keep only the top N.

## Common stages

| Stage           | SQL analogue                                |
|-----------------|---------------------------------------------|
| `$match`        | `WHERE`                                     |
| `$project`      | `SELECT col1, col2 AS new`                  |
| `$group`        | `GROUP BY` + aggregates                     |
| `$sort`         | `ORDER BY`                                  |
| `$limit`/`$skip`| `LIMIT`/`OFFSET`                            |
| `$unwind`       | flatten arrays into separate rows           |
| `$lookup`       | `LEFT JOIN` another collection              |
| `$addFields`    | compute new fields without removing old     |
| `$count`        | one document with a count                   |
| `$facet`        | run multiple pipelines and merge results    |
| `$out`/`$merge` | write the pipeline output to a collection   |

## Group operators

Inside `$group`, expressions starting with `$` refer to fields:

```javascript
{ $group: {
    _id: "$country",
    n: { $sum: 1 },
    total: { $sum: "$amount" },
    avg: { $avg: "$amount" },
    customers: { $addToSet: "$customer" }
} }
```

`$sum: 1` is the idiom for `COUNT(*)`.

## $project — shape the output

```javascript
{ $project: {
    _id: 0,
    customer: 1,
    year: { $year: "$createdAt" },
    revenue: "$amount"
} }
```

Computed fields use **aggregation expressions**: `$year`, `$add`, `$multiply`, `$concat`, `$cond` (ternary), `$switch`, and dozens more.

## $unwind — explode arrays

If an order has `items: [...]` and you want one document per item:

```javascript
[
  { $match: { _id: ObjectId("...") } },
  { $unwind: "$items" }
]
```

Combined with `$group`, this is how you do per-item analytics from order documents.

## $lookup — joining collections

```javascript
db.orders.aggregate([
  { $lookup: {
      from: "users",
      localField: "customer",
      foreignField: "_id",
      as: "userDoc"
  } },
  { $unwind: "$userDoc" }
]);
```

`$lookup` is slower than a SQL join, but it works. Use it when denormalizing would cost more than the join.

## $facet — multi-pipeline

Need counts AND a top-10 in one round trip?

```javascript
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $facet: {
      total:  [ { $count: "n" } ],
      top10:  [ { $sort: { amount: -1 } }, { $limit: 10 } ]
  } }
]);
```

## Performance tips

- Put `$match` first — pipelines can use indexes for the leading stages.
- Avoid `$lookup` if you can — embed instead, or fetch separately in application code.
- Use `explain("executionStats")` on aggregations too:
  ```javascript
  db.orders.aggregate([...], { explain: true })
  ```
