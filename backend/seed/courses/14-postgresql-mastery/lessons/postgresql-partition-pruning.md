# Exercise: Partition Pruning Simulator

Understand how PostgreSQL's query planner eliminates irrelevant partitions by implementing partition pruning logic yourself.

## Background

When you partition a table by `RANGE`, PostgreSQL stores each range of rows in a separate child table. The planner uses the partition key bounds together with the `WHERE` clause to determine which child tables can possibly contain matching rows — this is **partition pruning**.

```sql
CREATE TABLE events (
    id         bigint,
    created_at timestamptz NOT NULL,
    payload    jsonb
) PARTITION BY RANGE (created_at);

CREATE TABLE events_q1_2025 PARTITION OF events
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE events_q2_2025 PARTITION OF events
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE events_q3_2025 PARTITION OF events
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE events_q4_2025 PARTITION OF events
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');
```

A query like:

```sql
SELECT * FROM events
WHERE created_at >= '2025-04-01' AND created_at < '2025-07-01';
```

...allows the planner to prune `events_q1_2025`, `events_q3_2025`, and `events_q4_2025`, scanning only `events_q2_2025`.

Verify with `EXPLAIN`:

```
Append  (cost=...)
  ->  Seq Scan on events_q2_2025  (cost=...)
        Filter: (...)
```

## Pruning Rules

For a partition `[low, high)` and a query condition:

| Condition | Partition scanned when |
|---|---|
| `key = val` | `low <= val < high` |
| `key < val` | `low < val` |
| `key > val` | `high > val + 1` |
| `key <= val` | `low <= val` |
| `key >= val` | `high > val` |

## Why Partition Key in WHERE Matters

Partition pruning only works when the `WHERE` clause filters on the **partition key**. If you filter by a different column, all partitions must be scanned:

```sql
-- Pruning works: partition key in WHERE
SELECT * FROM events WHERE created_at > '2025-06-01';

-- NO pruning: different column
SELECT * FROM events WHERE payload->>'type' = 'click';
```

## Common Pitfalls

- **Over-partitioning**: thousands of partitions dramatically increases planning time; aim for tens to low hundreds
- **Missing default partition**: without a default partition, rows outside all defined ranges are rejected with an error
- **Unique constraints must include the partition key**: Postgres cannot enforce global uniqueness across partitions with a standard unique index

## Reference

- [PostgreSQL Official Documentation — Declarative Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)
- [PostgreSQL Tutorial — Partitioning](https://www.postgresqltutorial.com/postgresql-administration/postgresql-partitions/)

## Your Task

Given partition definitions and query conditions, determine which partitions the planner must scan. See the prompt for the full specification.
