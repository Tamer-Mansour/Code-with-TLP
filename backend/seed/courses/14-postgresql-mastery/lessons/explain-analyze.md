# Reading EXPLAIN ANALYZE

`EXPLAIN ANALYZE` runs your query and shows the actual execution plan with real timings — the single most important Postgres performance tool.

## Basic usage

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT *
FROM orders
WHERE customer_id = 42 AND status = 'paid';
```

The flags worth knowing:

| Option        | Adds                                             |
|---------------|--------------------------------------------------|
| `ANALYZE`     | Runs the query, includes real row counts/times.  |
| `BUFFERS`     | Cache hit/read counts. Reveals IO load.          |
| `VERBOSE`     | Column lists per node.                           |
| `SETTINGS`    | Any non-default GUC the planner saw.             |
| `FORMAT JSON` | Machine-readable (good for tools).               |

**Use `ANALYZE` with care on mutations** — `EXPLAIN ANALYZE UPDATE/DELETE` runs the statement. Wrap in a transaction and roll back:

```sql
BEGIN;
EXPLAIN ANALYZE UPDATE ... ;
ROLLBACK;
```

## Reading a plan

Plans are trees. Indented children feed their parent:

```
Sort  (cost=... rows=... width=...) (actual time=12.3..12.5 rows=23 loops=1)
  Sort Key: created_at DESC
  Sort Method: quicksort  Memory: 25kB
  ->  Index Scan using ix_orders_cust on orders  (cost=...)
        Index Cond: (customer_id = 42)
        Filter: (status = 'paid')
        Rows Removed by Filter: 117
```

What to look at:

1. **`actual time`** — the real cost. Last number is total time at this node.
2. **`rows`** — actual rows produced. Compare to `estimated rows` (in `cost=`). >10x off means stale statistics.
3. **`loops`** — node executed this many times (e.g., once per row in a nested loop). Total time = `time per loop * loops`.
4. **Method** — `Index Scan`, `Bitmap Heap Scan`, `Seq Scan`, etc.

## Plan node primer

| Node                    | When you see it                          |
|-------------------------|------------------------------------------|
| Seq Scan                | Full table read. Fine on small tables.   |
| Index Scan              | Direct B-tree walk, one match at a time. |
| Index Only Scan         | Covered query, doesn't touch heap.       |
| Bitmap Heap Scan        | Many index matches, batched fetch.       |
| Nested Loop             | For each row in outer, probe inner.      |
| Hash Join               | Build a hash on one side, probe.         |
| Merge Join              | Both sides sorted, walk in step.         |
| Sort                    | Explicit sort step. Watch the memory.    |
| Aggregate               | GROUP BY / aggregate functions.          |
| Materialize             | Cache a subquery's output.               |
| Subquery Scan / CTE Scan| CTE or subquery boundary.                |

## Red flags

- **Estimate vs actual mismatched 10× or more** → `ANALYZE table_name;`
- **Seq Scan on a big table for a selective WHERE** → missing index.
- **`Rows Removed by Filter` huge** → index returned too much; widen the index or add a partial.
- **Sort spilling to disk** (`Sort Method: external merge  Disk: 12345kB`) → increase `work_mem` for the session, or index away the sort.
- **Hash Join with batches > 1** → memory too small for the build side.
- **Buffer reads (`read`) high** → not in cache; the buffer pool's cold for this data.

## A worked optimization

Before:

```sql
EXPLAIN ANALYZE SELECT * FROM events WHERE payload->>'type' = 'login';
-- Seq Scan, 28s, rows: 230 of 50,000,000
```

Fix:

```sql
CREATE INDEX ix_events_type ON events ((payload->>'type'));
```

After:

```sql
-- Index Scan, 1.4ms, rows: 230
```

## auto_explain

For ongoing visibility, enable auto_explain to capture slow plans automatically:

```sql
LOAD 'auto_explain';
SET auto_explain.log_min_duration = '500ms';
SET auto_explain.log_analyze = on;
```

Slow queries land in the server log with their actual plans. Saves you from "can't reproduce" debugging sessions.
