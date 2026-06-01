# Aggregates and GROUP BY

Aggregate functions reduce many rows to one value. The big five:

| Function       | What it does                          |
|----------------|---------------------------------------|
| `COUNT(*)`     | Number of rows                        |
| `COUNT(col)`   | Number of non-NULL values in `col`    |
| `SUM(col)`     | Sum of numeric column                 |
| `AVG(col)`     | Arithmetic mean                       |
| `MIN`, `MAX`   | Smallest / largest value              |

## Without GROUP BY

A query with only aggregates returns a single row:

```sql
SELECT COUNT(*) AS users, MAX(created_at) AS latest FROM users;
```

## With GROUP BY

`GROUP BY` partitions rows into buckets, and the aggregate runs *per bucket*.

```sql
SELECT country, COUNT(*) AS n
FROM users
GROUP BY country
ORDER BY n DESC;
```

Rule of thumb: every column in `SELECT` is either an aggregate or appears in `GROUP BY`. (Strict MySQL mode enforces this — sloppy mode lets it slide and you can get nonsense results.)

## HAVING filters groups

`WHERE` runs before grouping (filters rows). `HAVING` runs after grouping (filters groups).

```sql
SELECT country, COUNT(*) AS n
FROM users
WHERE created_at >= '2025-01-01'    -- filter rows first
GROUP BY country
HAVING COUNT(*) > 100;              -- then filter aggregated buckets
```

## COUNT vs SUM with conditions

A handy idiom — count rows matching a condition using `SUM(condition)`:

```sql
SELECT
  COUNT(*)               AS total,
  SUM(status = 'paid')   AS paid,
  SUM(status = 'failed') AS failed
FROM orders;
```

Each `status = 'paid'` evaluates to `0` or `1`, and `SUM` adds them up.

## DISTINCT

```sql
SELECT COUNT(DISTINCT user_id) FROM orders;  -- unique customers
```

## A worked example

You have an `orders` table:

```
id | user_id | amount | status | created_at
```

Question: **What's the average paid order amount per country, for the last 30 days?**

```sql
SELECT u.country, AVG(o.amount) AS avg_amount, COUNT(*) AS n_orders
FROM orders o
JOIN users  u ON u.id = o.user_id
WHERE o.status = 'paid'
  AND o.created_at >= CURDATE() - INTERVAL 30 DAY
GROUP BY u.country
ORDER BY avg_amount DESC;
```

## Window functions (preview)

If you need per-row results *and* an aggregate (e.g., each order with the running total per user), reach for window functions instead of `GROUP BY`. MySQL 8 supports them:

```sql
SELECT
  user_id, created_at, amount,
  SUM(amount) OVER (PARTITION BY user_id ORDER BY created_at) AS running_total
FROM orders;
```

We cover window functions in detail later — they're one of the highest-leverage features added in MySQL 8.
