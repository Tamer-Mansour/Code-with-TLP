# Slow Query Log and Performance Schema

Knowing that a query is slow is only half the battle — you need to find which query is the culprit. MySQL ships two complementary tools: the **slow query log** for capturing slow queries as they run, and the **Performance Schema** for real-time instrumentation of the server's internals.

## Slow Query Log

The slow query log records any query that takes longer than `long_query_time` seconds (default: 10). Enable it in `my.cnf` (or `my.ini` on Windows):

```ini
[mysqld]
slow_query_log          = 1
slow_query_log_file     = /var/log/mysql/slow.log
long_query_time         = 1       # capture queries > 1 second
log_queries_not_using_indexes = 1 # also log full-table scans
```

Or enable it at runtime without restarting:

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

A typical slow log entry:

```
# Time: 2025-03-10T14:22:05.123456Z
# Query_time: 3.421  Lock_time: 0.000  Rows_sent: 120  Rows_examined: 9000000
SELECT * FROM events WHERE city = 'Cairo' ORDER BY created_at DESC LIMIT 120;
```

`Rows_examined` is the key number: 9 million rows scanned to return 120 means a missing index.

### mysqldumpslow

Parse and summarize the slow log with the bundled `mysqldumpslow` tool:

```bash
# Top 10 slowest queries by total time
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log
```

The **Percona pt-query-digest** tool is more powerful — it groups similar queries, shows percentile latencies, and can read binary logs.

## Performance Schema

The Performance Schema (`performance_schema` database) is a low-overhead in-memory instrumentation layer built into MySQL 5.6+. It collects statistics on waits, statements, stages, and memory usage.

### Most useful tables

| Table | What it tracks |
|---|---|
| `events_statements_summary_by_digest` | Normalized queries, total/average latency, rows examined |
| `events_waits_summary_global_by_event_name` | What the server waits on (I/O, locks, network) |
| `table_io_waits_summary_by_table` | Per-table read/write wait times |
| `memory_summary_global_by_event_name` | Memory allocation by component |

Find the worst queries by total execution time:

```sql
SELECT
    DIGEST_TEXT,
    COUNT_STAR          AS executions,
    SUM_TIMER_WAIT / 1e12 AS total_sec,
    AVG_TIMER_WAIT / 1e12 AS avg_sec,
    SUM_ROWS_EXAMINED
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;
```

### sys schema

MySQL 5.7+ ships the **`sys` schema** — a set of views and procedures built on top of Performance Schema that make the raw data human-readable:

```sql
-- Top 10 statements by total latency
SELECT * FROM sys.statement_analysis LIMIT 10;

-- Tables with the most full scans
SELECT * FROM sys.schema_tables_with_full_table_scans LIMIT 10;

-- Indexes that have never been used
SELECT * FROM sys.schema_unused_indexes;
```

## Workflow: finding and fixing a slow query

1. Enable `slow_query_log` with `long_query_time = 1`.
2. Run `mysqldumpslow` or `pt-query-digest` after a representative traffic period.
3. Take the worst offender and run `EXPLAIN` on it.
4. Add or adjust an index, then re-run `EXPLAIN` to confirm the plan improved.
5. Monitor `sys.statement_analysis` over the next day to verify the average latency dropped.
