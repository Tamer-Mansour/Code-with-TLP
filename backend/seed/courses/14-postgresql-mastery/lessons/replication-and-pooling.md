# Streaming Replication and pgBouncer

Two operational patterns you'll meet in any non-trivial Postgres deployment.

## Streaming replication

A **standby** server connects to the primary, requests WAL since its last applied position, and replays it. It can serve read-only queries (**hot standby**).

```
[ Primary ]  --stream WAL-->  [ Standby 1 (read-only) ]
                          \-> [ Standby 2 (read-only) ]
```

### Setup outline

On the primary:

```conf
# postgresql.conf
wal_level = replica
max_wal_senders = 10
wal_keep_size = '1GB'
```

```conf
# pg_hba.conf
host replication repuser 10.0.0.0/24 md5
```

```sql
CREATE ROLE repuser WITH REPLICATION LOGIN PASSWORD '...';
```

On the standby, base-backup from the primary then start:

```bash
pg_basebackup -h primary -D /var/lib/postgresql/16/data -U repuser -R
```

`-R` writes a `standby.signal` file and a `primary_conninfo` line — the standby boots in recovery mode and starts streaming.

### Synchronous vs asynchronous

```conf
# primary
synchronous_standby_names = 'standby1'
```

With sync replication, a `COMMIT` on the primary doesn't return until the standby has the WAL. Strongest durability, but standby outage = primary stalls. Most setups use async + multiple standbys for the right trade-off.

### Failover

If the primary dies, you promote a standby:

```bash
pg_ctl promote -D /var/lib/postgresql/16/data
```

Production deployments automate this with **Patroni** (the de facto Postgres HA tool) or **repmgr**. They use a distributed consensus store (etcd, Consul, ZooKeeper) for leader election.

### Logical replication

A different mechanism — replicates *changes to specific tables* via publish/subscribe rather than block-level WAL:

```sql
-- on primary
CREATE PUBLICATION pub_users FOR TABLE users;

-- on subscriber
CREATE SUBSCRIPTION sub_users
CONNECTION 'host=primary user=repuser dbname=shop'
PUBLICATION pub_users;
```

Use for: zero-downtime major version upgrades, cross-database integration, capturing changes for ETL.

## Connection pooling with pgBouncer

Every Postgres connection is a forked OS process. With thousands of idle connections you'll exhaust RAM. **pgBouncer** is a lightweight C proxy that pools connections.

```
clients (thousands)  →  pgBouncer  →  Postgres (50 backend procs)
```

### Pool modes

| Mode          | When a client gets a backend                    | Caveats                                |
|---------------|-------------------------------------------------|----------------------------------------|
| `session`     | For the whole client session                    | Same as no pooling capacity-wise       |
| `transaction` | For each transaction                            | **Recommended.** No sessions state.    |
| `statement`   | For each statement                              | Breaks anything spanning statements    |

`transaction` is the right mode for nearly every web app — but it means you can't use session-level features like prepared statements (without the `support_prepared_statements` setting in pgBouncer 1.21+), `LISTEN/NOTIFY`, or session-set GUCs.

### Config sketch

```ini
[databases]
shop = host=db.internal port=5432 dbname=shop

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type   = scram-sha-256
auth_file   = /etc/pgbouncer/userlist.txt
pool_mode   = transaction
max_client_conn = 5000
default_pool_size = 50
```

Now your app points at `pgbouncer:6432` instead of `postgres:5432`. The DB itself only sees 50 connections.

### When to skip pgBouncer

- You only have a few hundred connections.
- You depend on session features.
- You're on a managed service that already provides pooling (Neon, Supabase) — they often run it transparently.

For everyone else, pgBouncer is a near-mandatory companion to Postgres in production.
