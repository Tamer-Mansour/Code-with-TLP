# Index Lookup Simulation

Indexes are the most important performance tool in MySQL. An index is a separate data structure that MySQL maintains alongside a table to answer certain queries without scanning every row.

## How a B-tree index works

InnoDB stores indexes as **B-trees** (balanced trees). Each leaf node holds an indexed key value and a pointer to the corresponding table row. When you run:

```sql
SELECT * FROM users WHERE email = 'alice@example.com';
```

MySQL walks the B-tree in `O(log n)` steps to find the leaf that matches the email, then fetches that single row. Without an index, MySQL would scan every row: `O(n)`.

## What makes a good index candidate

Index columns that appear in:
- `WHERE` clauses with equality or range conditions
- `JOIN ... ON` conditions (especially the right-hand table)
- `ORDER BY` clauses (can eliminate a sort step)

Do NOT blindly index every column. Each index adds overhead to `INSERT`, `UPDATE`, and `DELETE` because MySQL must keep all indexes consistent.

## This exercise: simulating an index lookup

Real B-tree behavior is complex, but the key property is simple: **sorted order enables binary search**. Given a sorted list of `(key, value)` pairs (simulating an index), answer lookup queries using binary search — the same algorithmic principle MySQL uses.

For each query key:
- If found: return the value.
- If not found: return `NOT FOUND`.

This directly models `SELECT value FROM table WHERE key = ?` on an indexed column.

## Real MySQL commands

```sql
-- Create an index
CREATE INDEX ix_users_email ON users(email);

-- Drop an index
DROP INDEX ix_users_email ON users;

-- See all indexes on a table
SHOW INDEX FROM users;

-- See if a query uses an index
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';
```

## Further reading

- *MIT OCW 6.830: Database Systems* — B-tree indexes lecture — https://ocw.mit.edu/courses/6-830-database-systems-fall-2010/
- *CS50's Introduction to Databases with SQL*, Harvard — https://pll.harvard.edu/course/cs50s-introduction-databases-sql
