# Query Store

Query Store is SQL Server's built-in query performance history — think of it as a flight recorder for your queries. Available from SQL Server 2016, it persists execution statistics and query plans to the user database itself, surviving restarts.

## Why Query Store?

Before Query Store, plan regressions were hard to diagnose: a query ran fine for months, then an update changed statistics or caused a plan recompilation and suddenly it runs 10× slower. Without plan history you could not easily see *what changed*.

Query Store solves this by:
- Storing every compiled plan along with runtime statistics (duration, CPU, I/O, memory).
- Letting you compare plans for the same query over time.
- Letting you **force a specific plan** if a regression occurs — no code change needed.

## Enabling Query Store

```sql
ALTER DATABASE SalesDB SET QUERY_STORE = ON;

-- Configure retention (example: 30-day history, 100 MB max size)
ALTER DATABASE SalesDB SET QUERY_STORE (
    OPERATION_MODE      = READ_WRITE,
    CLEANUP_POLICY      = (STALE_QUERY_THRESHOLD_DAYS = 30),
    MAX_STORAGE_SIZE_MB = 100,
    QUERY_CAPTURE_MODE  = AUTO    -- AUTO ignores trivial/infrequent queries
);
```

Query Store is enabled **per database**. In SQL Server 2022 it is enabled by default on new databases.

## Checking the Status

```sql
SELECT name,
       is_query_store_on,
       desired_state_desc,
       actual_state_desc,
       current_storage_size_mb,
       max_storage_size_mb
FROM sys.databases
WHERE name = DB_NAME();
```

## Useful Query Store Queries

### Top Queries by Average CPU

```sql
SELECT TOP 10
    q.query_id,
    qt.query_sql_text,
    rs.avg_cpu_time / 1000.0    AS avg_cpu_ms,
    rs.avg_duration  / 1000.0   AS avg_duration_ms,
    rs.count_executions,
    rs.avg_logical_io_reads
FROM sys.query_store_query           AS q
JOIN sys.query_store_query_text      AS qt ON qt.query_text_id = q.query_text_id
JOIN sys.query_store_plan            AS p  ON p.query_id       = q.query_id
JOIN sys.query_store_runtime_stats   AS rs ON rs.plan_id       = p.plan_id
ORDER BY rs.avg_cpu_time DESC;
```

### Queries with Multiple Plans (Regression Candidates)

```sql
SELECT q.query_id,
       qt.query_sql_text,
       COUNT(DISTINCT p.plan_id) AS plan_count
FROM sys.query_store_query       AS q
JOIN sys.query_store_query_text  AS qt ON qt.query_text_id = q.query_text_id
JOIN sys.query_store_plan        AS p  ON p.query_id       = q.query_id
GROUP BY q.query_id, qt.query_sql_text
HAVING COUNT(DISTINCT p.plan_id) > 1
ORDER BY plan_count DESC;
```

## Forcing a Plan

If you identify a good plan from Query Store history, force it to prevent the optimizer from switching away:

```sql
-- @query_id and @plan_id from the queries above
EXEC sys.sp_query_store_force_plan
    @query_id = 42,
    @plan_id  = 7;
```

To release a forced plan:

```sql
EXEC sys.sp_query_store_unforce_plan
    @query_id = 42,
    @plan_id  = 7;
```

## SSMS GUI

SSMS ships with built-in Query Store reports under **Databases > your_db > Query Store**:

| Report | Use |
|--------|-----|
| Regressed Queries | Queries whose performance worsened recently |
| Top Resource Consuming Queries | Sort by CPU, duration, I/O, memory |
| Tracked Queries | Monitor specific queries over time |
| Plan Summary | All plans for a given query on a timeline |

## Automatic Plan Correction (SQL Server 2017+)

SQL Server can auto-force the last known good plan when it detects a regression:

```sql
ALTER DATABASE SalesDB SET AUTOMATIC_TUNING (FORCE_LAST_GOOD_PLAN = ON);
```

Monitor automatic corrections:

```sql
SELECT reason, score, details
FROM sys.dm_db_tuning_recommendations
WHERE state_transition_reason = 'AutomaticTuningOptionEnabled';
```
