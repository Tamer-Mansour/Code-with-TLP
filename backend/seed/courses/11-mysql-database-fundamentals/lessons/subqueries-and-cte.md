# Subqueries and CTEs

A **subquery** is a `SELECT` nested inside another statement. A **CTE** (Common Table Expression) is the same idea, named and pulled out front with `WITH`.

## Subquery in WHERE

```sql
-- Users who placed at least one order
SELECT * FROM users
WHERE id IN (SELECT DISTINCT user_id FROM orders);
```

`IN (subquery)` returns true if the value matches any row produced by the inner query.

## Subquery in SELECT (scalar subquery)

```sql
SELECT
  u.id, u.name,
  (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS n_orders
FROM users u;
```

It must return exactly one value per outer row.

## Subquery in FROM (derived table)

```sql
SELECT t.country, t.avg_age
FROM (
  SELECT country, AVG(age) AS avg_age
  FROM users
  GROUP BY country
) AS t
WHERE t.avg_age > 30;
```

You're treating the inner result as if it were a table.

## EXISTS vs IN

```sql
-- IN form
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE status = 'paid');

-- EXISTS form (often faster, especially with correlated subqueries)
SELECT * FROM users u
WHERE EXISTS (
  SELECT 1 FROM orders o
  WHERE o.user_id = u.id AND o.status = 'paid'
);
```

`EXISTS` short-circuits — the moment it finds one matching row it stops looking.

## Correlated subqueries

A correlated subquery references the outer query (`u.id` above). MySQL has to run it once per outer row — potentially slow on big tables. When you see one, ask if a `JOIN` would be cleaner and faster.

## CTEs — `WITH`

CTEs let you name a subquery and use it once or many times:

```sql
WITH paid_users AS (
  SELECT DISTINCT user_id FROM orders WHERE status = 'paid'
)
SELECT u.*
FROM users u
JOIN paid_users p ON p.user_id = u.id;
```

Use CTEs to:

- Break a complex query into readable steps.
- Reuse a derived set multiple times.
- Express recursion (`WITH RECURSIVE ...`).

## Recursive CTE (preview)

Walking a tree (e.g., comments with parent IDs):

```sql
WITH RECURSIVE thread AS (
  SELECT id, parent_id, body, 0 AS depth FROM comments WHERE id = 1
  UNION ALL
  SELECT c.id, c.parent_id, c.body, t.depth + 1
  FROM comments c
  JOIN thread t ON c.parent_id = t.id
)
SELECT * FROM thread ORDER BY depth;
```

## When to prefer JOIN over subquery

If you're filtering or shaping rows from related tables, **a `JOIN` is usually clearer and as fast or faster** than `IN (subquery)`. Subqueries shine when you need an aggregate condition (`HAVING COUNT > 5`) or are computing a single scalar value to compare against.
