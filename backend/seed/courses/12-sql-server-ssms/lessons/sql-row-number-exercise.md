# Exercise: Simulate the ROW_NUMBER Window Function

Window functions operate on a set of rows **related to the current row** without collapsing them into a single summary row. `ROW_NUMBER()` assigns a unique sequential integer to each row within a partition.

## The T-SQL Pattern

```sql
SELECT
    department,
    name,
    salary,
    ROW_NUMBER() OVER (
        PARTITION BY department
        ORDER BY salary DESC
    ) AS row_num
FROM dbo.employees
ORDER BY department, row_num;
```

- `PARTITION BY department` — reset the row number counter for each department
- `ORDER BY salary DESC` — rank employees within the department by salary, highest first
- The result: within each department, the highest earner gets `row_num = 1`

## ROW_NUMBER vs RANK vs DENSE_RANK

| Function | Behavior on ties |
|----------|-----------------|
| `ROW_NUMBER()` | Always unique — ties get arbitrary but distinct numbers (1, 2, 3) |
| `RANK()` | Ties share the same rank, next rank skips (1, 1, 3) |
| `DENSE_RANK()` | Ties share the same rank, no gaps (1, 1, 2) |

## Common Use Case: Top-N per Group

```sql
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY department
               ORDER BY salary DESC
           ) AS rn
    FROM dbo.employees
)
SELECT * FROM ranked WHERE rn <= 3;
```

This pattern — CTE with ROW_NUMBER + WHERE filter — is one of the most common patterns in production SQL Server queries. It replaces complex self-joins that were necessary before window functions existed.

## PARTITION BY Is Optional

Without `PARTITION BY`, the window covers the entire result set:

```sql
ROW_NUMBER() OVER (ORDER BY salary DESC)
```

This numbers all employees globally by salary, not per department.

## Performance Note

Window functions are evaluated **after** the WHERE clause and JOIN, but **before** ORDER BY and SELECT. They cannot be filtered in the same WHERE clause — you must wrap them in a CTE or subquery first (as shown in the Top-N pattern above).

## In This Exercise

You will assign ROW_NUMBER within each department, ordered by salary descending. Ties in salary maintain stable input order (the first employee encountered in input gets the lower row number). Output is sorted by department alphabetically, then by row_num ascending.

> **Further reading:** *SQL Notes for Professionals* (GoalKicker) — Chapter on window functions with examples — free at https://books.goalkicker.com/SQLBook/
