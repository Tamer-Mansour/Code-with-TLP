# T-SQL String Functions

SQL Server ships with a rich set of string functions. Knowing them saves you from pulling data into application code just to manipulate it.

## Core Functions

```sql
SELECT LEN('hello world')              -- 11 (characters, not bytes)
SELECT DATALENGTH(N'hello')            -- 10 (bytes for nvarchar: 2 per char)
SELECT UPPER('sql server')             -- 'SQL SERVER'
SELECT LOWER('SQL SERVER')             -- 'sql server'
SELECT LTRIM('  hi  ')                 -- 'hi  '
SELECT RTRIM('  hi  ')                 -- '  hi'
SELECT TRIM('  hi  ')                  -- 'hi'  (SQL Server 2017+)
```

## Substrings

```sql
SELECT SUBSTRING('abcdefg', 3, 4)     -- 'cdef'  (start at 3, take 4)
SELECT LEFT('hello', 3)               -- 'hel'
SELECT RIGHT('hello', 3)              -- 'llo'
SELECT CHARINDEX('lo', 'hello')       -- 4  (1-based position)
SELECT PATINDEX('%[0-9]%', 'abc123')  -- 4  (supports wildcards)
```

## Replacing and Splitting

```sql
SELECT REPLACE('hello world', 'world', 'SQL')   -- 'hello SQL'

-- STRING_SPLIT (SQL Server 2016+): returns a table
SELECT value
FROM   STRING_SPLIT('a,b,c,d', ',');
-- rows: a / b / c / d
```

## Concatenation

```sql
-- + operator: NULL propagates
SELECT 'hello' + ' ' + 'world'        -- 'hello world'
SELECT 'hello' + NULL                  -- NULL

-- CONCAT: treats NULL as empty string
SELECT CONCAT('hello', ' ', 'world')   -- 'hello world'
SELECT CONCAT('hello', NULL, 'world')  -- 'helloworld'

-- CONCAT_WS: with separator (SQL Server 2017+)
SELECT CONCAT_WS(', ', 'Alice', NULL, 'Bob')  -- 'Alice, Bob'
```

## Formatting Patterns

```sql
-- Zero-pad a number
SELECT FORMAT(42, '000')              -- '042'

-- Format a date as string
SELECT FORMAT(GETDATE(), 'yyyy-MM-dd')   -- '2025-06-01'

-- Repeat a string
SELECT REPLICATE('ab', 3)             -- 'ababab'

-- Space padding
SELECT STUFF('hello', 2, 3, '***')    -- 'h***o' (replace 3 chars starting at pos 2)
```

## STRING_AGG — Group Concatenation

Aggregate multiple rows into one delimited string (SQL Server 2017+):

```sql
SELECT
    customer_id,
    STRING_AGG(product_name, ', ') WITHIN GROUP (ORDER BY product_name) AS products
FROM dbo.order_items
GROUP BY customer_id;
```

Result example:

| customer_id | products |
|-------------|---------|
| 1 | Keyboard, Monitor, Mouse |
| 2 | Headset |

## Worked Example: Clean and Parse a Phone Column

```sql
-- Remove all non-digit characters from a phone field
SELECT id,
       -- Strip spaces, dashes, parentheses
       REPLACE(REPLACE(REPLACE(REPLACE(phone, ' ', ''), '-', ''), '(', ''), ')', '')
           AS clean_phone
FROM dbo.contacts;
```

For more complex cleaning, a scalar function or CLR function (C# in-database) is cleaner, but the above pattern covers most real-world data hygiene tasks without leaving T-SQL.

## Quick Reference Table

| Function | Purpose |
|----------|---------|
| `LEN` | Character count |
| `SUBSTRING(s, start, len)` | Extract substring |
| `CHARINDEX(find, source)` | Position of substring |
| `REPLACE(s, from, to)` | Find-and-replace |
| `STRING_SPLIT(s, delim)` | Split to rows |
| `STRING_AGG(col, delim)` | Rows to delimited string |
| `TRIM / LTRIM / RTRIM` | Strip whitespace |
| `CONCAT_WS(sep, ...)` | Join with separator, skip NULLs |
| `FORMAT(val, fmt)` | Culture-aware formatting |
