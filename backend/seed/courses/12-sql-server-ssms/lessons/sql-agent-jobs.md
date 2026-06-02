# SQL Server Agent Jobs

SQL Server Agent is the built-in scheduler for automating database tasks — backups, index maintenance, statistics updates, data archiving, and alert notifications. It runs as a Windows service and stores its configuration in the `msdb` system database.

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Job** | A named task with one or more steps and a schedule |
| **Step** | A unit of work: T-SQL, SSIS package, CmdExec, PowerShell |
| **Schedule** | When the job runs (one-time, recurring, or on SQL Server startup) |
| **Operator** | An email/pager address to notify on job success/failure |
| **Alert** | A rule that fires when a specific error number or performance condition occurs |

## Creating a Job via T-SQL

```sql
USE msdb;
GO

-- 1. Create the job
EXEC sp_add_job
    @job_name = N'NightlyIndexMaintenance',
    @enabled   = 1,
    @description = N'Rebuild/reorganize fragmented indexes on the sales database';

-- 2. Add a step
EXEC sp_add_jobstep
    @job_name      = N'NightlyIndexMaintenance',
    @step_name     = N'Rebuild Indexes',
    @subsystem     = N'TSQL',
    @command       = N'EXEC dbo.RebuildFragmentedIndexes;',  -- your custom proc
    @database_name = N'SalesDB',
    @on_success_action = 1,   -- 1 = Quit with success
    @on_fail_action    = 2;   -- 2 = Quit with failure

-- 3. Add a schedule (nightly at 02:00)
EXEC sp_add_schedule
    @schedule_name    = N'Daily2AM',
    @freq_type        = 4,      -- 4 = Daily
    @freq_interval    = 1,
    @active_start_time = 020000;  -- 02:00:00

EXEC sp_attach_schedule
    @job_name      = N'NightlyIndexMaintenance',
    @schedule_name = N'Daily2AM';

-- 4. Target the local server
EXEC sp_add_jobserver
    @job_name   = N'NightlyIndexMaintenance',
    @server_name = N'(local)';
GO
```

## Creating a Job via SSMS GUI

1. In Object Explorer, expand **SQL Server Agent > Jobs**.
2. Right-click **Jobs** and choose **New Job…**
3. Fill in the **General** tab (name, owner, description).
4. Go to **Steps**, click **New**, choose subsystem (T-SQL), write the command.
5. Go to **Schedules**, click **New**, set the recurrence.
6. Go to **Notifications**, configure email or event log on failure.
7. Click **OK**.

## Monitoring Job History

```sql
-- View recent job run history
SELECT
    j.name       AS job_name,
    h.run_date,
    h.run_time,
    h.run_duration,
    CASE h.run_status
        WHEN 0 THEN 'Failed'
        WHEN 1 THEN 'Succeeded'
        WHEN 2 THEN 'Retry'
        WHEN 3 THEN 'Cancelled'
        WHEN 4 THEN 'In Progress'
    END          AS status,
    h.message
FROM msdb.dbo.sysjobs    AS j
JOIN msdb.dbo.sysjobhistory AS h ON h.job_id = j.job_id
WHERE h.step_id = 0     -- 0 = the overall job outcome, not individual steps
ORDER BY h.run_date DESC, h.run_time DESC;
```

## Enabling Email Alerts (Database Mail)

SQL Server Agent sends notifications via **Database Mail**, which must be configured separately (SSMS > Management > Database Mail). Once configured:

```sql
-- Create an operator
EXEC msdb.dbo.sp_add_operator
    @name  = N'DBATeam',
    @email_address = N'dba-team@company.com';
```

Then reference the operator in the job's **Notifications** tab or `sp_update_job`.

## Common Automated Tasks

- **Nightly full backup** — `BACKUP DATABASE ... TO DISK`
- **Hourly transaction log backup** — `BACKUP LOG ... TO DISK`
- **Weekly index maintenance** — `ALTER INDEX ALL ON ... REBUILD/REORGANIZE`
- **Daily statistics update** — `EXEC sp_updatestats`
- **Archival** — move old rows from hot tables to archive tables
