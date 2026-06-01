# Window Functions in Postgres

A window function computes a value across a related set of rows **without collapsing** them. The window is defined by `OVER(...)`.

## Ranking

```sql
SELECT
  customer_id, amount,
  ROW_NUMBER() OVER w AS rn,
  RANK()       OVER w AS rk,
  DENSE_RANK() OVER w AS drk
FROM orders
WINDOW w AS (PARTITION BY customer_id ORDER BY amount DESC);
```

Reusable `WINDOW` clause keeps things DRY when you compute several functions over the same partition.

## Running totals and moving averages

```sql
SELECT
  created_at, amount,
  SUM(amount) OVER (ORDER BY created_at ROWS UNBOUNDED PRECEDING) AS running_total,
  AVG(amount) OVER (ORDER BY created_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7
FROM orders;
```

Two important pieces:

- **`ORDER BY`** inside `OVER` defines what "previous" means.
- **Frame clause** (`ROWS BETWEEN ...`) defines the window's bounds.

Frame variants:

| Frame                                          | Window contains                       |
|------------------------------------------------|---------------------------------------|
| `ROWS UNBOUNDED PRECEDING`                     | all rows from start through current   |
| `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`     | current + 6 before                    |
| `RANGE BETWEEN '1 day' PRECEDING AND CURRENT ROW` | rows whose ORDER BY value is within 1 day of current |
| `GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW`   | one peer group before + current peers |

`RANGE` with intervals (Postgres 11+) is fantastic for time-bucketed analytics without resampling.

## LAG and LEAD

```sql
SELECT
  created_at, amount,
  amount - LAG(amount) OVER (ORDER BY created_at) AS diff_from_prev,
  LEAD(created_at) OVER (ORDER BY created_at) AS next_event_at
FROM orders;
```

`LAG(x)` returns NULL on the first row; supply a default: `LAG(x, 1, 0)`.

## FIRST_VALUE, LAST_VALUE, NTH_VALUE

```sql
SELECT
  customer_id, created_at, amount,
  FIRST_VALUE(amount) OVER w AS first_order_amt,
  LAST_VALUE(amount)  OVER w AS last_order_amt
FROM orders
WINDOW w AS (
  PARTITION BY customer_id
  ORDER BY created_at
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
);
```

`LAST_VALUE` needs the explicit unbounded-following frame; otherwise it gives you the *current* row, which surprises everyone the first time.

## NTILE — buckets

```sql
SELECT
  customer_id, lifetime_value,
  NTILE(4) OVER (ORDER BY lifetime_value DESC) AS quartile
FROM customer_metrics;
```

Splits rows into N roughly equal-sized buckets — useful for percentile reporting.

## Top-N per group

```sql
WITH ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY category ORDER BY score DESC) AS rn
  FROM entries
)
SELECT * FROM ranked WHERE rn <= 3;
```

The canonical "top 3 per category" — solved in one window query.

## Performance

Window functions need either an index that matches the `ORDER BY`/`PARTITION BY`, or they'll sort. On big tables, an appropriate composite index makes them basically free.

`EXPLAIN (ANALYZE, BUFFERS)` shows the `WindowAgg` node and whether a `Sort` is feeding it. If you see a `Sort`, consider an index.
