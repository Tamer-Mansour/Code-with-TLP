# Index Maintenance and Fragmentation

Creating an index is the start, not the end. As data changes, indexes fragment — reads slow down and storage grows. SQL Server gives you the tools to monitor and fix fragmentation.

## What is Fragmentation?

When rows are inserted, updated, or deleted, SQL Server may split B-tree pages or leave pages with unused space. Two types matter:

| Type | Cause | Impact |
|------|-------|--------|
| **Logical fragmentation** | Pages in the index are out of logical order | Sequential scans read out-of-order pages, defeating read-ahead |
| **Page density / fill factor** | Pages are sparsely populated | More pages needed to store same data — larger scans |

## Checking Fragmentation

`sys.dm_db_index_physical_stats` is the go-to DMV:

```sql
SELECT
    OBJECT_NAME(ips.object_id)    AS table_name,
    i.name                        AS index_name,
    ips.avg_fragmentation_in_percent,
    ips.page_count
FROM sys.dm_db_index_physical_stats(
        DB_ID(),        -- current database
        NULL,           -- all tables
        NULL,           -- all indexes
        NULL,           -- all partitions
        'LIMITED'       -- mode: LIMITED is fast; SAMPLED or DETAILED are slower but more accurate
     ) AS ips
JOIN sys.indexes AS i
    ON i.object_id = ips.object_id
    AND i.index_id  = ips.index_id
WHERE ips.avg_fragmentation_in_percent > 5
  AND ips.page_count > 100
ORDER BY ips.avg_fragmentation_in_percent DESC;
```

## Fixing Fragmentation

### REORGANIZE (online, low impact)

Defragments leaf-level pages **in place**. Always online — users can keep reading and writing.

```sql
ALTER INDEX IX_orders_customer_id ON dbo.orders REORGANIZE;
```

Use when fragmentation is **5–30 %**.

### REBUILD (heavier, can be online in Enterprise Edition)

Drops and recreates the index from scratch. Compacts pages according to the fill factor.

```sql
-- Offline rebuild (Standard and Developer editions)
ALTER INDEX IX_orders_customer_id ON dbo.orders REBUILD;

-- Online rebuild (Enterprise edition only)
ALTER INDEX IX_orders_customer_id ON dbo.orders REBUILD WITH (ONLINE = ON);

-- Rebuild all indexes on a table
ALTER INDEX ALL ON dbo.orders REBUILD;
```

Use when fragmentation is **> 30 %**.

## Fill Factor

Fill factor (0–100) sets how full each leaf page is after a rebuild. A lower fill factor leaves space for future inserts, reducing page splits.

```sql
ALTER INDEX IX_orders_customer_id ON dbo.orders REBUILD WITH (FILLFACTOR = 80);
```

- **100** (default): pages completely full — good for read-heavy, rarely updated tables.
- **70–85**: common for tables with frequent inserts/updates.
- **50**: extreme — wastes storage, mainly useful for highly volatile tables.

## UPDATE STATISTICS

Statistics guide the query optimizer. They can go stale even without index fragmentation.

```sql
-- Update stats for one table
UPDATE STATISTICS dbo.orders;

-- Update stats for the whole database (use in maintenance window)
EXEC sp_updatestats;
```

SQL Server auto-updates statistics when about 20 % of rows change (500 rows for small tables), but heavy workloads benefit from scheduled manual updates.

## Maintenance Strategy (Rule of Thumb)

```
< 5 %  fragmentation  → do nothing
5–30 % fragmentation  → REORGANIZE + UPDATE STATISTICS
> 30 % fragmentation  → REBUILD (updates stats automatically)
```

Automate this with a SQL Server Agent job or Ola Hallengren's free **IndexOptimize** script (the industry standard for index maintenance on SQL Server).
