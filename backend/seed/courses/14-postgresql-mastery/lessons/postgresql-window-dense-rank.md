# Exercise: Window Function Dense Rank by Salary

Practice implementing PostgreSQL's `DENSE_RANK()` window function logic in Python.

## Background

Window functions in PostgreSQL compute a value for each row relative to a "window" of related rows — without collapsing the result set the way `GROUP BY` does. The `DENSE_RANK()` function assigns a sequential rank within each partition, with no gaps for ties.

```sql
SELECT
  name,
  department,
  salary,
  DENSE_RANK() OVER (
    PARTITION BY department
    ORDER BY salary DESC
  ) AS dense_rank
FROM employees
ORDER BY department, dense_rank, name;
```

**Ranking functions compared:**

| Function | Tie behavior | Example for scores 100, 100, 90 |
|---|---|---|
| `ROW_NUMBER()` | No ties — each row gets a unique number | 1, 2, 3 |
| `RANK()` | Ties share a rank, next rank skips | 1, 1, 3 |
| `DENSE_RANK()` | Ties share a rank, no gaps | 1, 1, 2 |

## Key Concepts

- `PARTITION BY department` resets the ranking for each department independently
- `ORDER BY salary DESC` means highest salary = rank 1
- When two rows have the same salary in the same department, they receive the same rank
- The next rank after a tie group is the next sequential integer (no skip)

## Reference

- [PostgreSQL Official Documentation — Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)
- [PostgreSQL Tutorial — Window Functions](https://www.postgresqltutorial.com/postgresql-window-function/) — includes live examples using the dvdrental database
- [PostgreSQL Notes for Professionals](https://books.goalkicker.com/PostgreSQLBook/) — Chapter on window functions with `RANK` vs `DENSE_RANK` comparison

## Your Task

Read employees from stdin, simulate `DENSE_RANK()` partitioned by department and ordered by salary descending, then print the results sorted by department, rank, and name. See the prompt for the full specification.
