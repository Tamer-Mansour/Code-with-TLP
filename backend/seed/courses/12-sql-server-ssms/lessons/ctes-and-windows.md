# CTEs and Window Functions

Two features that move you from beginner T-SQL to intermediate fast.

## Common Table Expressions

A CTE is a named, throwaway subquery:

```sql
WITH paid AS (
  SELECT * FROM dbo.orders WHERE status = 'paid'
)
SELECT customer_id, COUNT(*) AS n
FROM paid
GROUP BY customer_id;
```

You can chain multiple:

```sql
WITH
  paid AS (SELECT * FROM dbo.orders WHERE status = 'paid'),
  recent AS (SELECT * FROM paid WHERE created_at >= DATEADD(month, -1, GETDATE()))
SELECT * FROM recent;
```

CTEs are mostly **syntactic sugar** — the planner often inlines them. They make complex queries readable, which is the whole point.

## Recursive CTE

```sql
WITH RECURSIVE-style-in-tsql AS (    -- the keyword is just WITH; recursion is detected by UNION ALL
  SELECT id, parent_id, body, 0 AS depth
  FROM dbo.comments
  WHERE id = @root

  UNION ALL

  SELECT c.id, c.parent_id, c.body, t.depth + 1
  FROM dbo.comments c
  JOIN cte t ON c.parent_id = t.id
)
SELECT * FROM cte ORDER BY depth;
```

(Standard T-SQL drops the `RECURSIVE` keyword — recursion is implied.)

## Window functions

Aggregates that don't collapse rows. They compute a value across a **window** of rows defined by `OVER(...)`.

### Ranking

```sql
SELECT
  customer_id, amount,
  ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY amount DESC) AS rn,
  RANK()       OVER (PARTITION BY customer_id ORDER BY amount DESC) AS rk,
  DENSE_RANK() OVER (PARTITION BY customer_id ORDER BY amount DESC) AS drk
FROM dbo.orders;
```

- `ROW_NUMBER` → 1,2,3,4 unique per row
- `RANK` → 1,2,2,4 (gaps)
- `DENSE_RANK` → 1,2,2,3 (no gaps)

### Running totals and moving averages

```sql
SELECT
  customer_id, created_at, amount,
  SUM(amount) OVER (
    PARTITION BY customer_id
    ORDER BY created_at
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_total
FROM dbo.orders;
```

```sql
SELECT
  customer_id, created_at, amount,
  AVG(amount) OVER (
    PARTITION BY customer_id
    ORDER BY created_at
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS rolling_7
FROM dbo.orders;
```

### LAG and LEAD

Reach into the previous or next row:

```sql
SELECT
  created_at,
  amount,
  amount - LAG(amount) OVER (ORDER BY created_at) AS diff_from_prev
FROM dbo.orders;
```

### Why this matters

Before window functions you needed self-joins and clever subqueries for "Nth-per-group", "diff vs previous", or "rank by score". Now they're one line. Anything you've been doing with `ROW_NUMBER`+filter probably has a cleaner expression in window functions.

## Top-N per group with a window

```sql
WITH ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY category ORDER BY score DESC) AS rn
  FROM dbo.entries
)
SELECT * FROM ranked WHERE rn <= 3;
```

This is the pattern the upcoming exercise asks you to simulate in Python.
