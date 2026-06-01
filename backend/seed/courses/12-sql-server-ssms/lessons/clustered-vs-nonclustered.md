# Clustered vs Nonclustered Indexes

In SQL Server every table has **at most one clustered index** — it determines the **physical order** of rows on disk. If you defined a `PRIMARY KEY`, that's usually the clustered index unless you said otherwise.

A table with no clustered index is a **heap**: rows go wherever there's space. Heaps are rare in well-designed schemas.

## Clustered index = table data

```
Clustered index on id:
  Page 1: [1, ...] [2, ...] [3, ...]
  Page 2: [4, ...] [5, ...] [6, ...]
  ...
```

`WHERE id = 5` is a binary search down the index → straight to the row. Fast.

## Nonclustered index

A separate B-tree that maps `(indexed columns) → clustering key`. Looking up by email:

```
Nonclustered on email:
  ...→ alice@x.com → id=1
  ...→ bob@x.com   → id=4
```

Then SQL Server makes a **key lookup** into the clustered index to fetch the row. Two B-tree walks instead of one. Still fast if the lookup hits only a handful of rows.

## INCLUDE — covering nonclustered indexes

If you're constantly running:

```sql
SELECT id, name, email FROM dbo.users WHERE email = '...';
```

Add `INCLUDE` to make the index cover the query:

```sql
CREATE NONCLUSTERED INDEX ix_users_email
  ON dbo.users (email)
  INCLUDE (id, name);
```

Now SQL Server answers from the nonclustered index alone — no key lookup. **Covering indexes** are one of the biggest single-shot performance wins.

## Filtered indexes

Only index the rows you actually query:

```sql
CREATE NONCLUSTERED INDEX ix_users_active_email
  ON dbo.users (email)
  WHERE is_active = 1;
```

Smaller, cheaper to maintain.

## Index design rules of thumb

1. **One clustered index** — usually the PK, ideally narrow + monotonically increasing.
2. **Index every foreign key column.**
3. **Add nonclustered indexes for your top-N queries** — use `INCLUDE` to make them covering.
4. **Beware over-indexing** — every index slows down writes. Remove ones not used by `sys.dm_db_index_usage_stats`.

## Rebuilding and reorganizing

Fragmentation builds up as data churns. Periodic maintenance:

```sql
ALTER INDEX ALL ON dbo.users REBUILD;        -- full rebuild, more aggressive
ALTER INDEX ALL ON dbo.users REORGANIZE;     -- online, lighter
```

Or use Ola Hallengren's free maintenance solution — it's the de facto standard.

## Identifying missing indexes

```sql
SELECT TOP 20 *
FROM sys.dm_db_missing_index_details d
JOIN sys.dm_db_missing_index_groups g  ON g.index_handle = d.index_handle
JOIN sys.dm_db_missing_index_group_stats s ON s.group_handle = g.index_group_handle
ORDER BY s.avg_user_impact DESC;
```

SQL Server itself logs what indexes it wished it had. Read this list before guessing.
