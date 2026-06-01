# SQL Server Editions and Architecture

Microsoft SQL Server is a commercial relational database with a sprawling feature set: OLTP, OLAP, full-text search, in-memory tables, columnstore indexes, machine-learning services, geo-replication. You'll meet pieces of it slowly.

## Editions

| Edition       | Use for                                  |
|---------------|------------------------------------------|
| Express       | Free; 10 GB DBs, 1 CPU socket. Dev/test. |
| Developer     | Free; identical to Enterprise. Dev only. |
| Standard      | Mid-size production workloads.           |
| Enterprise    | Large production, all features unlocked. |
| Azure SQL DB  | Managed PaaS variant.                    |
| Azure SQL MI  | Managed Instance — closer to on-prem.    |

For learning, install **Developer Edition** locally — it's free and has every feature Enterprise has.

## Architecture, briefly

```
Client (SSMS, app)
   │  TDS protocol over port 1433
   ▼
SQL Server process
   ├── Query Engine (parser, optimizer, executor)
   ├── Storage Engine (buffer pool, transaction log)
   └── SQL Server Agent (scheduler for jobs)
        │
        ▼
   Data files (.mdf/.ndf) + Log file (.ldf)
```

Each database has at least one **data file** (`.mdf`) and one **transaction log** (`.ldf`). The log records every change and is the basis for crash recovery, point-in-time restore, and replication.

## System databases

- `master` — server-wide settings, login info. Back this up.
- `model` — template for new databases.
- `msdb` — SQL Server Agent jobs and history.
- `tempdb` — recreated on every restart; used for sort spills, temp tables, version store.

## Instances

A single host can run multiple **named instances**:

```
MYSERVER          ← default instance
MYSERVER\SQLDEV   ← named instance "SQLDEV"
```

Most laptops use one default instance and never think about it.

## Versioning vs. cadence

SQL Server is released roughly every two years (2016, 2017, 2019, 2022). Each is supported for 10 years. Look up the version of a running server:

```sql
SELECT @@VERSION;
SELECT SERVERPROPERTY('ProductVersion'), SERVERPROPERTY('Edition');
```

## What makes T-SQL different from MySQL/Postgres

A short list of friction points if you're coming from another dialect:

- `SELECT TOP 10 ...` instead of `LIMIT 10`.
- Identifier quoting is `[brackets]` (or double-quotes if `QUOTED_IDENTIFIER ON`).
- Stored procedures called with `EXEC`, parameters prefixed `@param`.
- `GETDATE()` for "now"; `SYSUTCDATETIME()` for UTC.
- `LEN()` instead of `LENGTH()`.
- Booleans don't exist as a first-class type — use `BIT`.

We'll meet these as we go.
