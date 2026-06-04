# Quiz: Performance and Diagnostics

Test your understanding of DMVs, Query Store, and diagnosing slow queries in SQL Server.

**Q1. What does a Dynamic Management View (DMV) expose?**
- [ ] User-defined query results stored at database creation
- [x] Internal SQL Server runtime state — query plans, wait stats, index usage, connections, and more
- [ ] The output of the last executed stored procedure
- [ ] Schema definitions for system tables

**Q2. Which DMV shows wait statistics that help identify the primary bottleneck (CPU, I/O, locks)?**
- [x] `sys.dm_os_wait_stats`
- [ ] `sys.dm_exec_query_stats`
- [ ] `sys.dm_db_index_usage_stats`
- [ ] `sys.dm_exec_sessions`

**Q3. Query Store's primary purpose is:**
- [ ] Caching query results for reuse
- [ ] Compressing execution plans to save space
- [x] Tracking query plans and runtime statistics over time so you can detect and force plan regressions
- [ ] Replacing the plan cache for all queries

**Q4. You want to find the top 10 queries by total CPU time since the last SQL Server restart. Which DMV is most useful?**
- [ ] `sys.dm_os_wait_stats`
- [x] `sys.dm_exec_query_stats` joined with `sys.dm_exec_sql_text`
- [ ] `sys.dm_db_missing_index_details`
- [ ] `sys.dm_exec_requests`

**Q5. Which Query Store view shows queries that have recently regressed (plan changed and performance got worse)?**
- [ ] Top Resource Consuming Queries
- [x] Regressed Queries
- [ ] Overall Resource Consumption
- [ ] Tracked Queries

**Q6. A query that was fast yesterday is slow today. Query Store shows two different plans for the same query hash. The recommended first action is:**
- [ ] Restart SQL Server to clear the plan cache
- [ ] Rebuild all indexes
- [x] Force the old, fast plan using Query Store's "Force Plan" feature
- [ ] Rewrite the query from scratch

**Q7. `sys.dm_db_index_usage_stats` is reset when:**
- [ ] A new query touches the index
- [ ] Any index is rebuilt
- [x] SQL Server service restarts (or the database is taken offline/online)
- [ ] The statistics are manually cleared with DBCC

**Q8. Which wait type typically indicates lock contention between concurrent sessions?**
- [ ] PAGEIOLATCH_SH
- [ ] SOS_SCHEDULER_YIELD
- [x] LCK_M_X (exclusive lock wait)
- [ ] ASYNC_NETWORK_IO

**Q9. The `sys.dm_exec_requests` DMV is most useful for:**
- [ ] Reviewing historical query performance over the past month
- [x] Seeing currently executing queries, their wait types, and blocking chains in real time
- [ ] Identifying missing indexes
- [ ] Reading backup history

**Q10. What does "parameter sniffing" mean in SQL Server?**
- [ ] SQL Server reads the query text character by character to find optimal keywords
- [ ] A security feature that inspects parameter values for injection attempts
- [x] SQL Server compiles a plan using the first set of parameter values it sees; the plan may perform poorly for very different parameter values used later
- [ ] Automatic query rewriting to use index hints
