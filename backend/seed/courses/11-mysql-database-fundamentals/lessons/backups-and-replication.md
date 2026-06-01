# Backups and Replication

If a database isn't backed up, it isn't really there. If it isn't replicated, a single hardware failure is downtime. Here are the basics.

## Logical backups with `mysqldump`

```bash
mysqldump --single-transaction --routines --triggers \
  -u root -p shop > shop_2025-06-01.sql
```

- `--single-transaction` uses an InnoDB consistent snapshot — no locking the whole DB.
- Output is a portable SQL script; restore with `mysql shop < shop_2025-06-01.sql`.

Pros: simple, portable, human-readable.
Cons: slow on big databases, restore is slow.

## Physical backups with Percona XtraBackup

For multi-hundred-GB databases, copy InnoDB files directly:

```bash
xtrabackup --backup --target-dir=/backup/$(date +%F)
xtrabackup --prepare --target-dir=/backup/2025-06-01
```

Much faster, and you can take incremental backups. Required tool for any serious self-hosted setup.

## Point-in-time recovery

Combine a full backup with **binary logs** to roll forward to any moment:

```
[Sunday full backup]  +  [binlog Sun..Tue 14:33]  =  state at Tue 14:33
```

Replay binlogs with `mysqlbinlog`:

```bash
mysqlbinlog --start-datetime='2025-06-01 09:00:00' \
            --stop-datetime='2025-06-01 14:33:00' \
            mysql-bin.000123 | mysql -u root -p
```

## Binary logging

Enable in `my.cnf`:

```
[mysqld]
server_id      = 1
log_bin        = mysql-bin
binlog_format  = ROW
sync_binlog    = 1
```

`ROW` format records before/after row images — safest for replication; `STATEMENT` records the SQL; `MIXED` picks per statement.

## Replication

The classic primary-replica setup:

```
[ Primary ] --writes binlog-->  [ Replica 1 ]
                            \-> [ Replica 2 ]
```

Replicas pull binlog events and replay them. Use replicas for:

- Read scaling (route reads to replicas).
- Backups (without slowing the primary).
- Failover targets.

Setup outline:

1. On the primary, create a replication user with `REPLICATION SLAVE` privilege.
2. Snapshot the primary (XtraBackup or `mysqldump`) and note the binlog position.
3. On the replica, restore the snapshot and `CHANGE REPLICATION SOURCE TO ...` pointing at the primary.
4. `START REPLICA;`
5. Watch `SHOW REPLICA STATUS\G` for `Seconds_Behind_Source` and any errors.

## Group Replication and InnoDB Cluster

MySQL 8 has built-in multi-primary support via Group Replication, packaged as **InnoDB Cluster**. Use it when you need automatic failover without bolting on Orchestrator or ProxySQL.

## Testing your backups

**A backup you haven't restored is not a backup.** Schedule monthly restore drills to a scratch server. Time the restore — that number is your worst-case RTO.

## Managed services

If you're on AWS RDS, Cloud SQL, Aurora, or PlanetScale, the platform handles binlog management, snapshots, point-in-time recovery, and replicas for you. You still need to verify that backups exist and restore tests pass.
