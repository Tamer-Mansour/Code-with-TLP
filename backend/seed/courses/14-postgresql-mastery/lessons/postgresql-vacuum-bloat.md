# Exercise: Simulate VACUUM — Dead Tuple Bloat

Practice understanding PostgreSQL's MVCC model by simulating the dead tuple accumulation that makes `VACUUM` necessary.

## Background

PostgreSQL never overwrites a row in-place. When you issue `UPDATE accounts SET balance = 100 WHERE id = 1`, the engine:

1. Writes a **new tuple** with the updated data and stamps it `xmin = current_transaction_id`
2. Marks the **old tuple** as dead by setting its `xmax = current_transaction_id`

The old tuple is invisible to new transactions but remains physically on disk until `VACUUM` removes it. The same happens with `DELETE` (no new tuple, just the xmax stamp).

```sql
-- After this UPDATE, the heap page contains two versions of the row:
UPDATE employees SET salary = 95000 WHERE id = 42;

-- View with the pageinspect extension:
SELECT lp, t_xmin, t_xmax, t_ctid FROM heap_page_items(get_raw_page('employees', 0));
-- lp | t_xmin | t_xmax | t_ctid
--  1 |    500 |    501 | (0,2)   <- dead: xmax is set
--  2 |    501 |      0 | (0,2)   <- live: xmax is 0
```

## Why This Matters

**Table bloat** is the ratio of dead tuples to total tuples. High bloat means:

- Heap pages full of invisible dead tuples, requiring more I/O to scan
- Index entries pointing at dead heap tuples, bloating indexes too
- `autovacuum` consuming CPU and I/O to clean up

Critical misconception: **`VACUUM` does NOT return disk space to the OS.** It marks dead tuple slots as reusable by future inserts within the same table. Only `VACUUM FULL` (which takes an exclusive lock and rewrites the entire table) actually shrinks the file on disk.

## Autovacuum Tuning

Default autovacuum triggers a vacuum when dead tuples exceed:

```
threshold = autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor * n_live_tup
-- default: 50 + 0.20 * n_live_tup
```

For high-churn tables (queues, event logs), the default 20% scale factor means autovacuum lags behind. Tune per-table:

```sql
ALTER TABLE hot_events SET (
  autovacuum_vacuum_scale_factor = 0.01,  -- trigger at 1% dead
  autovacuum_vacuum_cost_delay = 2        -- less throttling
);
```

## Reference

- [PostgreSQL Official Documentation — MVCC](https://www.postgresql.org/docs/current/mvcc.html)
- [PostgreSQL Tutorial — VACUUM](https://www.postgresqltutorial.com/postgresql-administration/postgresql-vacuum/) — with `pg_stat_user_tables` queries
- [PostgreSQL Notes for Professionals](https://books.goalkicker.com/PostgreSQLBook/) — Chapter on VACUUM, bloat, and autovacuum configuration

## Your Task

Simulate the MVCC heap: track live and dead tuples as INSERT and UPDATE operations arrive, then compute and print the bloat percentage. See the prompt for the full specification.
