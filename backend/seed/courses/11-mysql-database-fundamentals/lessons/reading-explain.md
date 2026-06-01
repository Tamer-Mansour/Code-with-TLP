# Reading EXPLAIN Output

`EXPLAIN` shows the **query plan** — how MySQL intends to execute a query. Reading it is the single most valuable skill for fixing slow SQL.

## Basic usage

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 1;
```

Output (simplified):

```
id  select_type  table   type   possible_keys  key                 rows  Extra
 1  SIMPLE       orders  ref    ix_orders_uid  ix_orders_user_id      3  Using index condition
```

Each column matters.

## Key columns

- **`type`** — the access strategy, ordered from best to worst:
  - `system` / `const` — looking up 0 or 1 row by PK or unique key.
  - `eq_ref` — at most one match per row from a joined table.
  - `ref` — index lookup on a non-unique key.
  - `range` — scanning a range of an index (`WHERE x BETWEEN ...`).
  - `index` — scanning the whole index.
  - **`ALL`** — full table scan. **Almost always the thing to fix.**
- **`key`** — which index was actually chosen.
- **`rows`** — estimated number of rows examined (lower is better).
- **`Extra`** — flags. Watch for:
  - `Using where` — applying a non-indexed filter; fine on small result sets.
  - `Using index` — covered by index, table not touched. Great.
  - `Using temporary` — building a temp table (often for `GROUP BY`); often slow.
  - `Using filesort` — sorting on disk/memory after the fact; not always bad but watch it.

## EXPLAIN ANALYZE

MySQL 8 actually runs the query and reports real timings:

```sql
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id)
FROM users u LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id;
```

Output includes `actual time=` per step — invaluable when the planner's estimates are off.

## A worked optimization

Before:

```sql
EXPLAIN SELECT * FROM orders WHERE customer_email = 'a@b.com';
-- type: ALL, rows: 5000000, Extra: Using where
```

Plan: full table scan. Fix:

```sql
CREATE INDEX ix_orders_email ON orders(customer_email);
```

After:

```sql
EXPLAIN SELECT * FROM orders WHERE customer_email = 'a@b.com';
-- type: ref, key: ix_orders_email, rows: 4
```

From 5 million rows examined to 4. That's a hundred-thousand-fold speedup.

## Force index (rarely needed)

The planner usually picks the right index. When it doesn't:

```sql
SELECT * FROM orders FORCE INDEX (ix_orders_email)
WHERE customer_email = 'a@b.com';
```

Treat this as a debugging tool. If you're shipping `FORCE INDEX` to production, usually the right fix is to update statistics (`ANALYZE TABLE`) or restructure the query.

## A workflow

1. Find the slow query (slow query log, `pt-query-digest`, `performance_schema`).
2. `EXPLAIN` it. Find the worst `type` row.
3. Look at `WHERE` columns and `JOIN` columns — are they indexed?
4. Add or restructure the index.
5. `EXPLAIN` again to confirm.
