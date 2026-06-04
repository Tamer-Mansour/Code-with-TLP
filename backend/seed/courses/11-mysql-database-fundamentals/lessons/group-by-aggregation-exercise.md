# GROUP BY Aggregation

Aggregation functions let you compute summary statistics across groups of rows — one of the most powerful and commonly used features in SQL analytics.

## The SQL this exercise models

```sql
SELECT
    product,
    COUNT(*) AS sale_count,
    ROUND(AVG(amount), 2) AS avg_amount
FROM sales
GROUP BY product
ORDER BY product;
```

This query groups all rows by product name, counts how many sales each product had, computes the average sale amount rounded to 2 decimal places, and returns the results sorted alphabetically.

## How GROUP BY works (logical execution order)

A critical concept beginners get wrong: SQL does **not** execute in the order it's written. The actual logical execution order is:

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

This is why you **cannot** use a `SELECT` alias in a `WHERE` clause — `WHERE` runs before `SELECT` assigns names. You **can** use aliases in `ORDER BY` because that runs after `SELECT`.

## Aggregate functions at a glance

| Function    | What it computes                            |
|-------------|---------------------------------------------|
| `COUNT(*)`  | Total rows in the group (includes NULLs)    |
| `COUNT(col)`| Rows where col is NOT NULL                  |
| `SUM(col)`  | Total of col values                         |
| `AVG(col)`  | Mean of col values (skips NULLs)            |
| `MIN(col)`  | Smallest value                              |
| `MAX(col)`  | Largest value                               |

## The HAVING clause

`WHERE` filters rows before grouping. `HAVING` filters groups after aggregation:

```sql
-- Only show products with more than 5 sales
SELECT product, COUNT(*) AS cnt
FROM sales
GROUP BY product
HAVING cnt > 5
ORDER BY product;
```

## Further reading

- *CS50's Introduction to Databases with SQL*, Harvard — https://pll.harvard.edu/course/cs50s-introduction-databases-sql
- *MIT OCW 1.264J*, Lecture 11: SQL Basics — https://ocw.mit.edu/courses/1-264j-database-internet-and-systems-integration-technologies-fall-2013/
