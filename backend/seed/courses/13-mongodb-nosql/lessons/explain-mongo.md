# explain() and Query Plans

`.explain()` is MongoDB's equivalent of SQL's `EXPLAIN`.

## Basic usage

```javascript
db.orders.find({ status: "paid" }).explain("executionStats");
```

Three verbosity levels:

| Verbosity            | What you get                                    |
|----------------------|-------------------------------------------------|
| `"queryPlanner"`     | Chosen plan only (default)                      |
| `"executionStats"`   | Runs the query and reports actual stats         |
| `"allPlansExecution"`| All considered plans + their stats              |

Use `executionStats` when investigating slowness.

## Key fields

```jsonc
{
  "queryPlanner": {
    "winningPlan": {
      "stage": "IXSCAN",        // or "COLLSCAN" - bad
      "indexName": "status_1",
      "keyPattern": { "status": 1 }
    }
  },
  "executionStats": {
    "executionTimeMillis": 4,
    "totalKeysExamined": 1000,
    "totalDocsExamined": 1000,
    "nReturned": 1000
  }
}
```

Healthy plans have:

- `stage: "IXSCAN"` — index scan.
- `totalKeysExamined ≈ nReturned` — index laser-focused on relevant entries.
- `totalDocsExamined ≈ nReturned` — or zero, for covered queries.

Warning signs:

- `stage: "COLLSCAN"` — full collection scan. Add an index.
- `totalDocsExamined >> nReturned` — your index narrows the work, but you still fetch many docs you discard. Often means a missing leading field.
- A `SORT` stage with `"sortPattern"` and a large `"memUsage"` — server is sorting in memory. Make the index match the sort order.

## Hint — force an index

```javascript
db.orders.find({ status: "paid" }).hint({ status: 1, createdAt: -1 });
```

Useful for *measuring* an alternative plan. If you ship `hint()` to production code, you're papering over a planner regression — investigate.

## Aggregations

```javascript
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $group: { _id: "$customer", total: { $sum: "$amount" } } }
], { explain: true });
```

Each stage shows up. Look for `$cursor.queryPlanner` — that's the underlying find that feeds the pipeline.

## Profiler

For ongoing visibility, the database profiler logs slow ops:

```javascript
db.setProfilingLevel(1, { slowms: 100 });
db.system.profile.find().sort({ ts: -1 }).limit(20);
```

Mostly used on staging; in production prefer **Database Profiler / Atlas Profiler / Performance Advisor**.

## A simple workflow

1. Identify a slow op via profiler / log / Atlas.
2. Reproduce it in a shell.
3. `.explain("executionStats")` — find COLLSCAN or oversize examined counts.
4. Add or restructure an index (ESR rule).
5. Re-explain. Confirm IXSCAN + tight ratios.
