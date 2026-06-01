# SELECT, WHERE, ORDER BY

The `SELECT` statement is the workhorse of SQL. Most of what you do in a database is shape this one statement.

## Shape of a SELECT

```sql
SELECT <columns>
FROM <table>
WHERE <row filter>
ORDER BY <sort>
LIMIT <n>;
```

Each clause is independent and optional (except `SELECT`). MySQL evaluates them in a fixed logical order:

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

That ordering matters: you can't use a `SELECT` alias in `WHERE`, but you *can* use one in `ORDER BY`.

## Picking columns

```sql
SELECT id, name, email FROM users;
SELECT * FROM users;        -- all columns, fine for exploration, not for code
SELECT name AS full_name FROM users;
```

Avoid `SELECT *` in production code — it makes queries fragile when columns change.

## WHERE: filtering rows

```sql
SELECT * FROM users WHERE id = 42;
SELECT * FROM users WHERE created_at >= '2025-01-01';
SELECT * FROM users WHERE name LIKE 'A%';        -- starts with A
SELECT * FROM users WHERE country IN ('US','CA','MX');
SELECT * FROM users WHERE deleted_at IS NULL;    -- not "= NULL" !
```

`NULL` comparisons always use `IS NULL` / `IS NOT NULL`. `x = NULL` is itself `NULL`, never true.

Combine with `AND`, `OR`, `NOT`:

```sql
SELECT * FROM orders
WHERE status = 'paid'
  AND total > 100
  AND created_at >= CURDATE() - INTERVAL 7 DAY;
```

## ORDER BY

```sql
SELECT * FROM users ORDER BY created_at DESC;
SELECT * FROM users ORDER BY country ASC, name ASC;
```

`NULL`s sort *first* in `ASC` and *last* in `DESC` on MySQL.

## LIMIT and OFFSET

```sql
SELECT * FROM events ORDER BY id DESC LIMIT 10;          -- newest 10
SELECT * FROM events ORDER BY id DESC LIMIT 10 OFFSET 20;-- the 21st–30th
```

Pagination via `OFFSET` gets slow on big tables — the server still walks past the skipped rows. **Keyset pagination** (`WHERE id < :last_seen ORDER BY id DESC LIMIT 10`) scales much better.

## Common gotchas

- String comparison in MySQL is **case-insensitive** by default (depends on collation). `'alice' = 'ALICE'` may be true.
- Comparing dates to strings works (`'2025-01-01'`) but be explicit with `DATE` literals when types matter.
- `ORDER BY RAND()` is convenient but O(n) — fine for tiny tables, terrible for big ones.

## Quick exercises (mental)

Predict the result of each before you run it:

```sql
SELECT 1 = 1, 1 = NULL, NULL = NULL;
SELECT 'abc' LIKE 'a%', 'abc' LIKE '_b_';
SELECT 5 IN (1, 2, 3, NULL);   -- NULL, not false
```

`IN` with a `NULL` doesn't match but also doesn't *not-match* — it returns `NULL`. This is a famous foot-gun.
