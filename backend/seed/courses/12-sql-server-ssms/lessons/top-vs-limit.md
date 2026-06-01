# TOP, OFFSET, and Pagination in T-SQL

T-SQL doesn't have `LIMIT`. You'll meet three ways to bound results: `TOP`, `OFFSET...FETCH`, and the older `ROW_NUMBER` trick.

## TOP

```sql
SELECT TOP 10 *
FROM dbo.orders
ORDER BY created_at DESC;
```

`TOP (n)` accepts a variable: `SELECT TOP (@page_size) ...`.

`TOP n PERCENT` returns the top `n` percent of rows.

`TOP n WITH TIES` returns ties at the boundary — useful for "top 10 scores including ties for 10th place":

```sql
SELECT TOP 10 WITH TIES name, score
FROM dbo.players
ORDER BY score DESC;
```

## OFFSET ... FETCH (SQL Server 2012+)

The standard, paginated form:

```sql
SELECT *
FROM dbo.orders
ORDER BY created_at DESC
OFFSET @page * @page_size ROWS
FETCH NEXT @page_size     ROWS ONLY;
```

`ORDER BY` is **required** — `OFFSET/FETCH` is a clause on it.

## Keyset pagination (recommended for large data)

`OFFSET` makes SQL Server scan and discard rows it's already returned. Slow on big tables. Prefer keyset pagination:

```sql
-- first page
SELECT TOP 20 *
FROM dbo.orders
ORDER BY id DESC;

-- next page: pass the last id you saw
SELECT TOP 20 *
FROM dbo.orders
WHERE id < @last_seen_id
ORDER BY id DESC;
```

It uses the index directly and runs in milliseconds even on billion-row tables.

## ROW_NUMBER

The pre-2012 idiom. Still useful for "the Nth-something per group":

```sql
WITH numbered AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY customer_id
           ORDER BY created_at DESC
         ) AS rn
  FROM dbo.orders
)
SELECT * FROM numbered WHERE rn = 1;       -- most recent order per customer
```

## A note on consistency

Without `ORDER BY`, the rows returned by `TOP`/`OFFSET` are *undefined*. The optimizer may pick whatever order is convenient — and that can change as your data grows or your indexes shift. Always pair `TOP`/`OFFSET` with an `ORDER BY` on a column with a unique tiebreaker (often the PK).

```sql
SELECT TOP 20 * FROM dbo.orders ORDER BY created_at DESC, id DESC;
```
