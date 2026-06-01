# CTEs and Recursive Queries

A Common Table Expression (CTE) names a subquery and lets you reference it like a table. Postgres CTEs are a workhorse — readable, composable, and recursive when you need them.

## Plain CTEs

```sql
WITH paid AS (
  SELECT * FROM orders WHERE status = 'paid'
)
SELECT customer_id, COUNT(*)
FROM paid
GROUP BY customer_id;
```

Chain multiple:

```sql
WITH
  paid       AS (SELECT * FROM orders WHERE status = 'paid'),
  this_month AS (SELECT * FROM paid WHERE created_at >= date_trunc('month', now()))
SELECT customer_id, SUM(amount)
FROM this_month
GROUP BY customer_id;
```

## CTE inlining

As of Postgres 12, the planner inlines a CTE by default — same performance as the equivalent subquery. Force the old "optimization fence" behavior with:

```sql
WITH paid AS MATERIALIZED (...)
```

Use `MATERIALIZED` if the CTE is called multiple times and computing it once is cheaper than recomputing.

## Writable CTEs

```sql
WITH archived AS (
  DELETE FROM events
  WHERE created_at < now() - interval '1 year'
  RETURNING *
)
INSERT INTO events_archive
SELECT * FROM archived;
```

You can chain `INSERT`, `UPDATE`, `DELETE` — each with `RETURNING` — into a single transactional statement.

## Recursive CTEs

For trees, graphs, and counting sequences:

```sql
WITH RECURSIVE thread AS (
  -- anchor: the root comment
  SELECT id, parent_id, body, 0 AS depth
  FROM comments
  WHERE id = 1

  UNION ALL

  -- recursive: children of anything in the set so far
  SELECT c.id, c.parent_id, c.body, t.depth + 1
  FROM comments c
  JOIN thread t ON c.parent_id = t.id
)
SELECT * FROM thread ORDER BY depth, id;
```

Anatomy:

- **Anchor query** — starting rows.
- **`UNION ALL`** — required, even if you mean `UNION`.
- **Recursive query** — references the CTE name (`thread`).
- **Termination** — happens when the recursive query produces 0 rows.

## Generate a sequence

```sql
WITH RECURSIVE numbers(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM numbers WHERE n < 10
)
SELECT * FROM numbers;
```

(Postgres has `generate_series(1, 10)` for this specific case — recursive CTEs shine for irregular sequences.)

## Date series for reports

```sql
SELECT day::date,
       COALESCE(SUM(amount), 0) AS revenue
FROM generate_series(date '2025-01-01', date '2025-12-31', interval '1 day') AS day
LEFT JOIN orders o ON o.created_at::date = day::date
GROUP BY day
ORDER BY day;
```

This gives you a row per day even when no orders occurred — gap-free reports.

## Guarding against infinite recursion

```sql
WITH RECURSIVE thread AS (
  SELECT ..., 0 AS depth FROM comments WHERE id = 1
  UNION ALL
  SELECT ..., t.depth + 1 FROM comments c JOIN thread t ON c.parent_id = t.id
  WHERE t.depth < 100   -- safety net
)
```

Always bound the depth when traversing user-supplied trees.
