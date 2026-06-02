# Table Partitioning in PostgreSQL

Partitioning splits one logical table into multiple physical child tables. Done right, it dramatically speeds up range queries and makes deleting old data nearly instant. Postgres supports native declarative partitioning since version 10.

## Why partition?

- **Query pruning**: the planner skips partitions that cannot contain matching rows, turning a full-table scan into a scan of one or two smaller chunks.
- **Bulk delete**: dropping an old partition (`DROP TABLE month_2022_01`) is near-instant, unlike `DELETE FROM events WHERE created_at < '2022-02-01'` on 100 million rows.
- **I/O locality**: frequently queried recent partitions fit in memory while cold partitions stay on disk.

## Partition strategies

| Strategy | Best for                                 | Example key           |
|----------|------------------------------------------|-----------------------|
| RANGE    | Time-series, sequential IDs              | `created_at`, `id`    |
| LIST     | Discrete values, low cardinality         | `region`, `status`    |
| HASH     | Even distribution, no natural range      | `user_id`             |

## Range partitioning — worked example

```sql
-- Parent table: no storage of its own
CREATE TABLE events (
    id          bigserial,
    created_at  timestamptz NOT NULL,
    type        text,
    payload     jsonb
) PARTITION BY RANGE (created_at);

-- Monthly partitions
CREATE TABLE events_2025_01
    PARTITION OF events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE events_2025_02
    PARTITION OF events
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Default partition catches anything outside defined ranges
CREATE TABLE events_default
    PARTITION OF events DEFAULT;
```

Inserts go to the correct child automatically. Queries with a `WHERE created_at BETWEEN` clause will only touch the relevant partition(s).

## Indexes on partitions

```sql
-- Creates an index on every existing (and future) partition
CREATE INDEX ON events (created_at);
CREATE INDEX ON events USING GIN (payload);
```

Each partition gets its own independent index — more flexible than a monolithic index.

## Partition pruning in action

```sql
EXPLAIN SELECT * FROM events
WHERE created_at >= '2025-02-01' AND created_at < '2025-03-01';
```

Look for `Partitions selected:` in the plan. Only `events_2025_02` should appear.

```
Append  (cost=...)
  ->  Seq Scan on events_2025_02  (cost=...)
        Filter: ((created_at >= '2025-02-01') AND (created_at < '2025-03-01'))
```

## Automating partition creation

Postgres does not auto-create future partitions. Use `pg_partman` (a popular extension) or a scheduled job:

```sql
-- Example: create next month's partition via a cron'd function
CREATE OR REPLACE FUNCTION create_monthly_partition(tbl text, start_date date)
RETURNS void AS $$
DECLARE
    partition_name text := tbl || '_' || to_char(start_date, 'YYYY_MM');
    next_date      date := start_date + interval '1 month';
BEGIN
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
        partition_name, tbl, start_date, next_date
    );
END;
$$ LANGUAGE plpgsql;
```

## Caveats

- **Primary keys and unique constraints must include the partition key.** A global unique index across all partitions is not supported natively (workaround: a separate unique table as a lookup).
- **Foreign keys into a partitioned table** are supported since Postgres 12 but each child table carries its own FK overhead.
- **Partition pruning requires the partition key in the WHERE clause** — filtering by a different column still scans all partitions.
- Over-partitioning (thousands of partitions) bloats the planner's work; aim for tens to low hundreds.
