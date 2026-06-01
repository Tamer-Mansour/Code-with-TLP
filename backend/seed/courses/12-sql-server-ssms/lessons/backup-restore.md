# Backup, Restore, and Recovery Models

A SQL Server database is only as safe as your last successful backup *and* your last successful restore test.

## Recovery models

Set per-database; controls how the transaction log is managed and what backup options you have.

| Model         | Log behavior                          | Point-in-time restore? |
|---------------|---------------------------------------|-----------------------|
| SIMPLE        | Log auto-truncates on checkpoint.     | No                    |
| FULL          | Log grows until backed up.            | **Yes**               |
| BULK_LOGGED   | Like FULL, but minimal log for bulk.  | Mostly                |

Production transactional DBs → **FULL**. Dev/test → SIMPLE.

```sql
ALTER DATABASE shop SET RECOVERY FULL;
```

## Backup types

- **Full** — entire database. Baseline for every recovery chain.
- **Differential** — everything changed since the last full. Smaller, faster.
- **Transaction log** — every committed change since the last log backup. Only in FULL.

## A common rotation

| Frequency | Type              |
|-----------|-------------------|
| Weekly    | Full              |
| Daily     | Differential      |
| Every 15m | Transaction log   |

That gives you ~15 minutes RPO and lets you restore to any point.

## Taking backups

```sql
BACKUP DATABASE shop
  TO DISK = 'D:\backups\shop_full.bak'
  WITH INIT, COMPRESSION, CHECKSUM, STATS = 10;
```

- `INIT` overwrites the file.
- `COMPRESSION` is enabled in Standard+ — much smaller files.
- `CHECKSUM` validates pages while reading.
- `STATS = 10` prints a progress line every 10%.

```sql
BACKUP DATABASE shop TO DISK = '...\diff.bak'
  WITH DIFFERENTIAL, COMPRESSION;

BACKUP LOG shop TO DISK = '...\log.trn'
  WITH COMPRESSION;
```

## Restoring

```sql
RESTORE DATABASE shop
  FROM DISK = 'D:\backups\shop_full.bak'
  WITH NORECOVERY;                   -- leaves DB in restoring state

RESTORE DATABASE shop
  FROM DISK = 'D:\backups\shop_diff.bak'
  WITH NORECOVERY;

RESTORE LOG shop
  FROM DISK = 'D:\backups\shop_log.trn'
  WITH STOPAT = '2025-06-01 14:33:00', RECOVERY;
```

`NORECOVERY` between steps lets you keep applying more files. `RECOVERY` on the last step brings the DB online.

## Test your restores

A backup you've never restored is a wish. Schedule monthly drills to a scratch server:

```sql
RESTORE DATABASE shop_test
  FROM DISK = '...'
  WITH MOVE 'shop'     TO 'D:\restore\shop_test.mdf',
       MOVE 'shop_log' TO 'D:\restore\shop_test.ldf',
       REPLACE;
```

Track the wall-clock time. That's your **RTO** under normal conditions.

## Backup verification

```sql
RESTORE VERIFYONLY FROM DISK = 'D:\backups\shop_full.bak';
```

Cheaper than a real restore; catches corrupt backup files.

## Always-On Availability Groups

For HA you usually pair backups with **Availability Groups** — multiple replicas of the DB across servers with synchronous or asynchronous commit. Detailed in advanced lessons; the short version: backups protect against data loss, AGs protect against downtime.

## DBCC CHECKDB

Schedule weekly:

```sql
DBCC CHECKDB (shop) WITH NO_INFOMSGS, ALL_ERRORMSGS;
```

Catches physical corruption *before* it's in every backup you've taken.
