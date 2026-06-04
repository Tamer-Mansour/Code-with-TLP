# Aggregation Pipeline Simulator

MongoDB's aggregation framework is one of its most powerful features. Understanding how pipeline stages chain together — filtering records, then grouping and summarizing them — is essential for building reports, dashboards, and analytics features.

## The Exercise

Simulate a two-stage aggregation pipeline. You receive N records in `category:value` format, then two pipeline stage commands:

1. `$match category=<X>` — keep only records whose category equals X.
2. `$group` — count the matched records and sum their values.

Print `count:<N>` and `sum:<total>` on separate lines.

## Example

Input:

```
5
fruit:10
vegetable:20
fruit:30
fruit:5
vegetable:15
$match category=fruit
$group
```

Output:

```
count:3
sum:45
```

## How MongoDB's Aggregation Pipeline Works

In MongoDB, a pipeline is an ordered array of stage objects. Documents flow through each stage, being filtered, transformed, or summarized:

```javascript
db.products.aggregate([
  { $match:  { category: "fruit" } },
  { $group:  { _id: null, count: { $sum: 1 }, total: { $sum: "$price" } } }
]);
```

The stages map directly to this exercise:

| MongoDB Stage | Exercise Equivalent |
|---------------|---------------------|
| `$match` | Filter records by category |
| `$group` with `$sum: 1` | Count matched records |
| `$group` with `$sum: "$value"` | Sum the value field |

## Core Aggregation Stages Reference

**`$match`** — filters documents (like SQL `WHERE`). Always put `$match` first to reduce the number of documents flowing to later stages.

```javascript
{ $match: { status: "active", age: { $gte: 18 } } }
```

**`$group`** — collapses documents into groups. The `_id` field defines the grouping key; `null` means "aggregate all":

```javascript
{ $group: {
    _id: "$category",
    count: { $sum: 1 },
    total: { $sum: "$price" },
    avg:   { $avg: "$price" }
} }
```

**`$sort`**, **`$limit`**, **`$skip`** — control ordering and pagination.

**`$project`** — reshapes documents, adding or removing fields.

**`$unwind`** — flattens arrays into individual documents.

**`$lookup`** — performs a left outer join against another collection.

## Performance Rule: Match Early

The single most important optimization in aggregation pipelines is placing `$match` before `$group` and `$project`. A `$match` at the start can use an index; a `$match` buried after a `$group` cannot.

```javascript
// Good: $match first
db.orders.aggregate([
  { $match: { year: 2025 } },      // uses index on "year"
  { $group: { _id: "$customer", total: { $sum: "$amount" } } }
]);

// Bad: $match after $group
db.orders.aggregate([
  { $group: { _id: "$customer", total: { $sum: "$amount" } } },
  { $match: { total: { $gt: 1000 } } }  // full scan of intermediate results
]);
```

## Further Reading

- Martin Fowler, *Introduction to NoSQL* (YouTube, 54 min): [https://www.youtube.com/watch?v=qI_g07C_Q5I](https://www.youtube.com/watch?v=qI_g07C_Q5I) — covers aggregate-oriented design, the philosophy behind grouping whole entities into documents.
- Christof Strauch, *NoSQL Databases*, §5.3 — Query Languages in Document Stores: [https://www.christof-strauch.de/nosqldbs.pdf](https://www.christof-strauch.de/nosqldbs.pdf)
