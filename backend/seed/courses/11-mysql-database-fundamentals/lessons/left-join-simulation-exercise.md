# LEFT JOIN Simulation

The `LEFT JOIN` is the most commonly used outer join in SQL. Understanding its exact semantics — including when it produces `NULL` — is essential for writing correct queries.

## What LEFT JOIN does

A `LEFT JOIN` returns every row from the **left** table. For each left row, MySQL looks for matching rows in the right table using the `ON` condition. If a match is found, the columns from the right table are included. If no match exists, right-table columns are filled with `NULL`.

```sql
SELECT a.id, a.value_a, b.value_b
FROM table_a a
LEFT JOIN table_b b ON b.id = a.id
ORDER BY a.id;
```

## Contrast with INNER JOIN

| Join type  | Rows returned                                    |
|------------|--------------------------------------------------|
| INNER JOIN | Only rows that match on both sides               |
| LEFT JOIN  | All rows from left + matched rows from right     |
| RIGHT JOIN | All rows from right + matched rows from left     |

The anti-join pattern (finding rows with NO match) uses LEFT JOIN + `WHERE right_col IS NULL`:

```sql
-- Find all users who have never placed an order
SELECT u.id, u.name
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id IS NULL;
```

## Common mistake: implicit WHERE filtering kills the outer join

```sql
-- BUG: this becomes an INNER JOIN because WHERE filters NULL rows out
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.amount > 100;   -- removes rows where amount IS NULL

-- CORRECT: push the filter into the ON clause
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id AND o.amount > 100;
```

## This exercise

You'll simulate MySQL's `LEFT JOIN` behavior in code: given two tables keyed by an integer `id`, produce the left-joined result sorted by `id`. Use the literal string `NULL` where the right table has no match.

## Further reading

- *CS50's Introduction to Databases with SQL*, Harvard — https://pll.harvard.edu/course/cs50s-introduction-databases-sql
- *MIT OCW 1.264J*, Lecture 13: SQL Joins and Subqueries — https://ocw.mit.edu/courses/1-264j-database-internet-and-systems-integration-technologies-fall-2013/
