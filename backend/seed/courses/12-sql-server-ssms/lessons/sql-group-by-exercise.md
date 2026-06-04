# Exercise: GROUP BY Aggregation

Aggregation is one of the core operations in SQL. You collapse multiple rows into summary rows using aggregate functions, grouped by one or more columns.

## The SQL Pattern

```sql
SELECT   region, SUM(amount) AS total_sales
FROM     dbo.sales
GROUP BY region
ORDER BY region;
```

`GROUP BY` partitions the result set into groups — one group per unique value of `region`. The `SUM` aggregate function then operates within each group.

## Key Aggregate Functions in T-SQL

| Function | Purpose |
|----------|---------|
| `COUNT(*)` | Number of rows in the group |
| `COUNT(col)` | Number of non-NULL values in the column |
| `SUM(col)` | Sum of all non-NULL values |
| `AVG(col)` | Average of all non-NULL values |
| `MIN(col)` | Smallest non-NULL value |
| `MAX(col)` | Largest non-NULL value |

## HAVING: Filtering After Aggregation

`WHERE` filters rows **before** grouping. `HAVING` filters **after** grouping:

```sql
SELECT   region, SUM(amount) AS total_sales
FROM     dbo.sales
WHERE    sale_date >= '2025-01-01'          -- filter rows first
GROUP BY region
HAVING   SUM(amount) > 10000               -- filter groups after aggregation
ORDER BY total_sales DESC;
```

A common mistake is putting an aggregate condition in `WHERE` — that causes an error. Always use `HAVING` for conditions on aggregated values.

## NULL Handling in Aggregates

Aggregate functions (except `COUNT(*)`) ignore NULLs. If a sales column contains NULLs, `SUM(amount)` sums only the non-NULL rows. `COUNT(*)` counts all rows; `COUNT(amount)` counts only rows where `amount` is not NULL.

## GROUP BY Gotcha: SELECT List Restriction

Every column in `SELECT` that is **not** inside an aggregate function **must** appear in `GROUP BY`. This is a frequent source of errors:

```sql
-- ERROR: 'name' is not in GROUP BY and not aggregated
SELECT region, name, SUM(amount) FROM dbo.sales GROUP BY region;

-- CORRECT:
SELECT region, SUM(amount) FROM dbo.sales GROUP BY region;
```

## In This Exercise

You will receive sales records with a region and an amount. Compute the total per region and output results sorted alphabetically by region name — mirroring `GROUP BY region ORDER BY region`.

> **Further reading:** *SQL Notes for Professionals* (GoalKicker) — Chapter on GROUP BY and aggregate functions, free at https://books.goalkicker.com/SQLBook/
