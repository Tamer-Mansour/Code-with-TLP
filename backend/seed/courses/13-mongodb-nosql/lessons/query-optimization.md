# Query Optimization and Performance Tuning

After you have indexes in place, the next step is validating that queries actually use them efficiently. MongoDB provides several tools for this.

## The explain() Method

`explain()` shows how MongoDB plans and executes a query. Three verbosity levels:

```javascript
// "queryPlanner" (default) — show the winning plan, no execution
db.orders.find({ customer: "alice" }).explain();

// "executionStats" — run the query and report actual stats
db.orders.find({ customer: "alice" }).explain("executionStats");

// "allPlansExecution" — show stats for ALL candidate plans considered
db.orders.find({ customer: "alice" }).explain("allPlansExecution");
```

## Reading executionStats

The key fields in the `executionStats` output:

| Field | Meaning | Goal |
|---|---|---|
| `nReturned` | Documents returned to the caller | — |
| `totalKeysExamined` | Index entries scanned | Should be close to `nReturned` |
| `totalDocsExamined` | Documents fetched from disk | Should be close to `nReturned` |
| `executionTimeMillis` | Query duration | As low as possible |

A healthy query has `totalDocsExamined / nReturned` close to 1. A ratio of 1000:1 means the query is scanning far more than it returns — a sign you need a better index.

## Recognizing Bad Stages

Look at the `winningPlan.stage` field:

```json
{
  "stage": "COLLSCAN",
  "filter": { "status": { "$eq": "paid" } }
}
```

- **`COLLSCAN`** — collection scan (no index). Bad for large collections.
- **`IXSCAN`** — index scan. Good.
- **`FETCH`** — load documents to check non-indexed fields. Acceptable if selective.
- **`SORT`** — in-memory sort. Expensive; add an index for the sort fields.
- **`SORT_KEY_GENERATOR`** — building sort keys without an index. See `SORT`.

A query plan you want to see: `IXSCAN → FETCH → PROJECTION`. A query plan you want to fix: `COLLSCAN` or `SORT` on a hot path.

## Forcing an Index (Hint)

MongoDB's query planner may choose a suboptimal index. You can override it:

```javascript
db.orders.find({ status: "paid" })
         .hint({ status: 1, createdAt: -1 })
         .explain("executionStats");
```

Never leave `hint()` in production code permanently — it prevents the planner from adapting. Use it during tuning to compare plans.

## Slow Query Log

The MongoDB profiler captures slow queries:

```javascript
// Enable profiling for queries slower than 100 ms
db.setProfilingLevel(1, { slowms: 100 });

// Read the profiler output
db.system.profile.find().sort({ ts: -1 }).limit(5).pretty();
```

Profiler level 0 = off, 1 = slow queries only, 2 = all queries (very verbose; dev only).

## Common Tuning Checklist

1. Run `explain("executionStats")` on every slow query.
2. If you see `COLLSCAN`, add an index on the filtered field.
3. If `totalDocsExamined >> nReturned`, your index is not selective enough — add more fields or reorder the compound index.
4. If you see `SORT` in the plan, include the sort fields in your index (ESR rule).
5. Check for **index intersection** — MongoDB can use two separate indexes, but a single compound index is almost always faster.
6. Look for `$or` — each clause needs its own index or MongoDB falls back to a collection scan.

## Connection Pool Sizing

Slow queries are not always index problems. Check if the connection pool is exhausted:

```javascript
db.serverStatus().connections
// { "current": 45, "available": 155, "totalCreated": 220 }
```

If `available` is near zero, increase the pool size in your driver configuration, scale horizontally, or add a read replica.
