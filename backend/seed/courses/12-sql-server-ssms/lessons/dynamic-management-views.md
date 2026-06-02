# Dynamic Management Views (DMVs)

Dynamic Management Views (DMVs) and Dynamic Management Functions (DMFs) expose the internal runtime state of SQL Server. They are the primary tool for diagnosing performance problems, monitoring waits, and understanding what the engine is actually doing.

## What DMVs Are

DMVs are system views prefixed with `sys.dm_`. They query in-memory structures — data disappears when the server restarts (or when internal counters reset). Always think of them as a snapshot of *right now*, not historical records.

```sql
-- List all available DMVs and DMFs
SELECT name, type_desc
FROM   sys.system_objects
WHERE  name LIKE 'dm_%'
ORDER BY name;
```

## Most Useful DMVs

### Active Connections and Sessions

```sql
SELECT
    s.session_id,
    s.login_name,
    s.status,
    s.cpu_time,
    s.logical_reads,
    s.last_request_start_time,
    r.blocking_session_id,
    r.wait_type,
    r.wait_time / 1000.0       AS wait_seconds,
    SUBSTRING(t.text, 1, 200)  AS sql_snippet
FROM       sys.dm_exec_sessions    AS s
LEFT JOIN  sys.dm_exec_requests    AS r ON r.session_id = s.session_id
OUTER APPLY sys.dm_exec_sql_text(r.sql_handle) AS t
WHERE s.is_user_process = 1
ORDER BY s.cpu_time DESC;
```

### Top Wait Types (Server-Wide)

Waits reveal *why* queries are slow. The highest-wait types point to the bottleneck.

```sql
SELECT TOP 20
    wait_type,
    waiting_tasks_count,
    wait_time_ms / 1000.0       AS total_wait_sec,
    max_wait_time_ms / 1000.0   AS max_wait_sec,
    signal_wait_time_ms / 1000.0 AS signal_wait_sec
FROM sys.dm_os_wait_stats
WHERE wait_type NOT IN (
    -- Filter out benign background waits (common exclusion list)
    'SLEEP_TASK', 'WAITFOR', 'BROKER_TO_FLUSH',
    'SQLTRACE_BUFFER_FLUSH', 'CLR_AUTO_EVENT',
    'DISPATCHER_QUEUE_SEMAPHORE', 'XE_DISPATCHER_WAIT',
    'REQUEST_FOR_DEADLOCK_SEARCH', 'LOGMGR_QUEUE',
    'CHECKPOINT_QUEUE', 'DBMIRROR_EVENTS_QUEUE'
)
ORDER BY wait_time_ms DESC;
```

Common problem wait types:

| Wait Type | Likely Root Cause |
|-----------|------------------|
| `PAGEIOLATCH_SH` | Disk I/O bottleneck — missing indexes or slow storage |
| `LCK_M_*` | Locking contention — long-running transactions |
| `SOS_SCHEDULER_YIELD` | CPU pressure |
| `ASYNC_NETWORK_IO` | Client reading results too slowly |
| `RESOURCE_SEMAPHORE` | Memory pressure on query workspace |

### Missing Index Suggestions

```sql
SELECT TOP 10
    mig.avg_total_user_cost * mig.avg_user_impact * (mig.user_seeks + mig.user_scans) AS improvement_score,
    mid.statement                   AS table_name,
    mid.equality_columns,
    mid.inequality_columns,
    mid.included_columns
FROM sys.dm_db_missing_index_groups    AS mig
JOIN sys.dm_db_missing_index_group_stats AS migs ON migs.group_handle = mig.index_group_handle
JOIN sys.dm_db_missing_index_details   AS mid  ON mid.index_handle   = mig.index_handle
WHERE mid.database_id = DB_ID()
ORDER BY improvement_score DESC;
```

### Expensive Queries (Cached Plans)

```sql
SELECT TOP 20
    total_logical_reads / execution_count AS avg_logical_reads,
    execution_count,
    total_elapsed_time / execution_count / 1000.0 AS avg_elapsed_ms,
    SUBSTRING(st.text, 1, 300) AS sql_snippet
FROM sys.dm_exec_query_stats AS qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
ORDER BY avg_logical_reads DESC;
```

### Index Usage Stats

```sql
SELECT
    OBJECT_NAME(i.object_id) AS table_name,
    i.name                   AS index_name,
    ius.user_seeks,
    ius.user_scans,
    ius.user_lookups,
    ius.user_updates,
    ius.last_user_seek
FROM sys.dm_db_index_usage_stats AS ius
JOIN sys.indexes                 AS i
    ON i.object_id = ius.object_id
    AND i.index_id  = ius.index_id
WHERE ius.database_id = DB_ID()
ORDER BY ius.user_seeks + ius.user_scans DESC;
```

Indexes with zero seeks and many updates are **unused** — they cost write overhead with no read benefit and are candidates for removal.

## Security Note

DMVs require `VIEW SERVER STATE` (most server-wide DMVs) or `VIEW DATABASE STATE` (database-scoped DMVs). Grant carefully — they expose query text, login names, and wait information.

```sql
GRANT VIEW SERVER STATE TO [monitoring_login];
```
