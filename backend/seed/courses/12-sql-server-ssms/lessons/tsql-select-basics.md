# T-SQL SELECT and Filters

T-SQL (Transact-SQL) is Microsoft's dialect. The basic `SELECT` is the same SQL you already know, with a few Microsoft-specific spices.

## SELECT shape

```sql
SELECT col1, col2
FROM   dbo.users
WHERE  is_active = 1
ORDER BY created_at DESC;
```

The `dbo.` prefix is the schema (default schema is `dbo` — "database owner"). Always qualify table names — it removes ambiguity and helps the planner.

## TOP

```sql
SELECT TOP 10 *
FROM   dbo.users
ORDER BY created_at DESC;
```

`TOP (n)` may be a constant or a variable: `SELECT TOP (@n) ...`.

## Identifiers

```sql
SELECT [order id], [user name] FROM dbo.[order log];
```

Brackets quote identifiers — needed for names with spaces, reserved words, or non-alphanumeric characters. Double-quotes also work if `QUOTED_IDENTIFIER ON` (the default).

## Strings and dates

```sql
SELECT 'O''Brien' AS name;                 -- escape ' by doubling
SELECT N'unicode';                         -- N prefix = nchar literal
SELECT GETDATE(), SYSUTCDATETIME();        -- now (local), now (UTC)
SELECT DATEADD(day, -7, GETDATE());        -- 7 days ago
SELECT DATEDIFF(day, '2025-01-01', GETDATE());
SELECT FORMAT(GETDATE(), 'yyyy-MM-dd');
```

Use `SYSUTCDATETIME()` and store UTC. Always.

## Conditional expressions

`CASE` is your friend:

```sql
SELECT id,
       CASE
         WHEN amount >= 100 THEN 'big'
         WHEN amount >= 10  THEN 'medium'
         ELSE                    'small'
       END AS bucket
FROM dbo.orders;
```

`IIF` is shorthand:

```sql
SELECT IIF(amount > 100, 'big', 'small');
```

## NULL helpers

```sql
SELECT ISNULL(nickname, 'Anonymous');      -- T-SQL specific
SELECT COALESCE(nickname, name, 'N/A');    -- standard SQL, accepts any number of args
```

`ISNULL(a, b)` returns `a` if not null else `b`; `COALESCE` returns the first non-null.

## Set operators

```sql
SELECT email FROM dbo.customers
UNION                                       -- distinct
SELECT email FROM dbo.prospects;

SELECT id FROM dbo.a
INTERSECT
SELECT id FROM dbo.b;

SELECT id FROM dbo.a
EXCEPT                                      -- in a, not in b
SELECT id FROM dbo.b;
```

`UNION ALL` is faster than `UNION` if you don't need de-duplication.

## SELECT INTO

T-SQL specific — create a new table from a query in one step:

```sql
SELECT * INTO dbo.users_backup FROM dbo.users;
```

Great for quick snapshots before risky updates.
