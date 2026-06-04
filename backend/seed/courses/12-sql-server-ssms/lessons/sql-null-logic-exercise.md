# Exercise: NULL-Safe Comparison (Three-Valued Logic)

One of the most important rules in SQL — and one of the most commonly misunderstood — is how NULL values work.

## NULL Is Not a Value

NULL represents the **absence of a value**. It is not zero, not an empty string, not `false`. Because of this, any arithmetic or comparison involving NULL produces NULL (not TRUE or FALSE):

```sql
NULL = NULL     -- evaluates to UNKNOWN, not TRUE
NULL <> NULL    -- evaluates to UNKNOWN, not TRUE
NULL = 0        -- evaluates to UNKNOWN
NULL + 5        -- evaluates to NULL
```

This is called **three-valued logic**: a predicate can be `TRUE`, `FALSE`, or `UNKNOWN`.

## The WHERE Clause Requires TRUE

The `WHERE` clause only passes rows where the predicate evaluates to **TRUE**. Rows where the predicate is `FALSE` or **UNKNOWN** are excluded.

```sql
-- This returns NO rows even if NULLs exist in the column:
SELECT * FROM dbo.products WHERE price = NULL;

-- This correctly finds rows with a NULL price:
SELECT * FROM dbo.products WHERE price IS NULL;

-- This correctly finds rows with a non-NULL price:
SELECT * FROM dbo.products WHERE price IS NOT NULL;
```

## Common Mistakes

```sql
-- WRONG — always returns 0 rows regardless:
WHERE manager_id = NULL

-- CORRECT:
WHERE manager_id IS NULL

-- WRONG — also misses NULLs:
WHERE NOT (manager_id = 5)   -- NULLs are excluded by UNKNOWN

-- CORRECT — explicitly handle NULLs:
WHERE manager_id <> 5 OR manager_id IS NULL
```

## NULL Helpers in T-SQL

```sql
-- Replace NULL with a default:
SELECT ISNULL(price, 0) AS price FROM dbo.products;

-- ANSI standard (accepts more than 2 args):
SELECT COALESCE(price, list_price, 0) AS effective_price FROM dbo.products;

-- Conditional NULL — NULLIF returns NULL if both args are equal:
SELECT NULLIF(qty, 0) AS qty FROM dbo.stock;   -- avoids divide-by-zero
```

## In This Exercise

Each row has a product name and an optional price. The string `'NULL'` represents a SQL NULL (a missing value). You will classify each row as `Priced` or `Unpriced` — mirroring how a SQL query using `IS NULL` vs `IS NOT NULL` behaves.

> **Key correction:** Comparing NULL with `=` always produces UNKNOWN, which is treated as FALSE in a WHERE clause. **Never use `= NULL`; always use `IS NULL`.**

> **Further reading:** *Microsoft SQL Server Notes for Professionals* (GoalKicker) covers NULL, COALESCE, and ISNULL extensively — free at https://books.goalkicker.com/MicrosoftSQLServerBook/
