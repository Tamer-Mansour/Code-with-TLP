# LATERAL Joins

A `LATERAL` join lets a subquery on the right side of a `JOIN` reference columns from the table on the left. It's like a for-each-row in SQL.

## The motivating problem

"For each user, return their three most recent orders." Without `LATERAL` you'd write a window function or a correlated subquery in `SELECT`. With `LATERAL`:

```sql
SELECT u.id, u.name, o.*
FROM users u
JOIN LATERAL (
  SELECT * FROM orders
  WHERE orders.user_id = u.id
  ORDER BY created_at DESC
  LIMIT 3
) o ON true;
```

The subquery executes once per row in `users`, with `u.id` available inside. The `ON true` is conventional — the actual relationship lives in the subquery's `WHERE`.

## Why this is useful

- "Top N per group" without window functions (and often faster).
- Joining table functions per row: `JOIN LATERAL unnest(arr) AS x ON true`.
- Computing intermediate values reused in `SELECT`/`WHERE`:

```sql
SELECT u.id, m.total_orders, m.total_spend
FROM users u
LEFT JOIN LATERAL (
  SELECT COUNT(*) AS total_orders, SUM(amount) AS total_spend
  FROM orders
  WHERE user_id = u.id
) m ON true;
```

## INNER vs LEFT LATERAL

- `JOIN LATERAL ... ON true` — drops users with no matching orders.
- `LEFT JOIN LATERAL ... ON true` — keeps them, NULL-filling the right side.

Use `LEFT` when "no rows on the right" is a valid case (most of the time).

## With table functions

`generate_series` and `unnest` shine here:

```sql
SELECT u.id, day::date
FROM users u
JOIN LATERAL generate_series(
  u.created_at::date,
  current_date,
  interval '1 day'
) day ON true;
```

One row per user per day they've existed.

## Performance notes

- `LATERAL` runs the right-hand side once per left row. Index the columns it references.
- Often the planner is smart enough to push filters and limits — `EXPLAIN ANALYZE` to confirm.

## When NOT to use it

For "this exists in another table" use `EXISTS`. For "give me a list of related rows", `JOIN` is fine. `LATERAL` shines when you need a *bounded per-row computation* (top-N, table function expansion, derived aggregates per row).
