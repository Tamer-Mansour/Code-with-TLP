# WAL, Backups, and Point-in-Time Recovery

The **Write-Ahead Log (WAL)** is the heart of Postgres durability and replication. Every change is written to WAL before it touches data files. On crash, replaying WAL brings the cluster back to consistency.

## Why WAL?

Synchronous fsyncs on every page write would crawl. Instead Postgres:

1. Writes a WAL record (sequential, fast).
2. Modifies the page in memory (`shared_buffers`).
3. Eventually flushes the dirty page during checkpoints.

If the server crashes between steps 2 and 3, WAL replays step 2 on startup. Durability without the IO cost.

## WAL files

WAL lives in `PGDATA/pg_wal/`. Files are 16 MB each (default), named with a hex stamp. They're recycled or archived as they fill.

```sql
SELECT pg_current_wal_lsn();
SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') AS bytes_written;
```

## Backup options

### `pg_dump` — logical backup

```bash
pg_dump -Fc -f shop.dump shop
pg_restore -d shop_restored shop.dump
```

- **`-Fc`** = custom format. Compressed, supports parallel restore, can extract individual tables.
- Locks aren't a problem — `pg_dump` uses a serializable snapshot.

Great for: schema migrations, dev/test data, moving small databases.
Not great for: huge databases (slow), point-in-time recovery (can't).

### `pg_basebackup` — physical base backup

```bash
pg_basebackup -D /backup/base -Ft -z -P
```

Copies the data directory at a consistent WAL position. Pair with archived WAL for PITR.

### Continuous archiving + PITR

The production setup:

```conf
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'rclone copy %p remote:wal/%f && [exit 0]'
```

After every WAL file is filled, `archive_command` runs to ship it to durable storage (S3, GCS, NFS).

For recovery you have:
- A base backup (from `pg_basebackup`).
- All WAL files from the moment the base backup started.

To restore to any moment:

```conf
# recovery.signal + postgresql.auto.conf
restore_command = 'rclone copy remote:wal/%f %p'
recovery_target_time = '2025-06-01 14:33:00'
```

Postgres replays WAL from the base up to the target time, then opens.

## Tooling

Don't roll your own. Use one of:

- **pgBackRest** — battle-tested, supports parallel + delta backups.
- **WAL-G** — modern, cloud-storage-aware.
- **Barman** — full lifecycle backup manager.

Managed services (RDS, Crunchy, Neon, Supabase) handle this for you — but you still need to verify and time test restores.

## Test your backups

The bullet point you'll see in every DB chapter, because it matters: **a backup you've never restored is not a backup.**

Schedule monthly restore drills to a scratch server. Time the restore — that's your worst-case RTO.

## What WAL gives you besides durability

- **Replication.** Streaming replication sends WAL to standby servers (covered next).
- **Point-in-time recovery.**
- **Logical decoding** for change data capture (Debezium, Kafka Connect).
- **Auditing** — `pgaudit` writes WAL-derived events for compliance.
