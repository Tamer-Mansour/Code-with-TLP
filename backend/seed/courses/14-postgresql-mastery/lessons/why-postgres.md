# Why PostgreSQL?

PostgreSQL (often just "Postgres") is a free, open-source, ACID-compliant relational database with a 35-year history and an unusually deep feature set. If you're starting a new project and don't have a specific reason to pick something else, Postgres is the right default.

## What sets it apart

- **Standards compliance.** Closer to ANSI SQL than MySQL or SQL Server.
- **Rich type system.** JSON / JSONB, arrays, ranges, geometric types, full-text search, UUID, custom types.
- **Extensions.** Per-database plugins for geospatial (PostGIS), time-series (TimescaleDB), full-text (`pg_trgm`), search (`pg_search`), and dozens more.
- **Concurrency model (MVCC).** Readers never block writers; writers never block readers.
- **Honest about what it is.** Postgres doesn't truncate strings, doesn't silently coerce types, and doesn't lie about constraint violations.

## What it's not great at

- **Scaling writes horizontally** without an extension (Citus) or a rewrite into multi-tenant sharding.
- **Drop-in replacement for analytical workloads** at petabyte scale (use ClickHouse, Snowflake, BigQuery).
- **In-memory caching** speed (use Redis).

## Architecture in one diagram

```
client (psql, app)
   │  libpq over port 5432
   ▼
postmaster      ← one process per connection (or pooled)
   ├── backend
   ├── backend
   ├── autovacuum
   ├── wal writer
   └── checkpointer
       │
       ▼
   data files  +  WAL  +  shared_buffers
```

Each connection gets its own OS process. That's why you almost always run a **connection pooler** (pgBouncer) in front of Postgres — otherwise 10,000 idle web requests = 10,000 processes.

## Default ports and files

- Listens on TCP **5432** by default.
- Cluster lives in `PGDATA` (often `/var/lib/postgresql/<ver>/main`).
- `postgresql.conf` — main config.
- `pg_hba.conf` — host-based authentication rules.

## Versions and EOL

Major versions release annually each fall (16 in 2023, 17 in 2024, 18 in 2025). Each is supported for 5 years. Upgrade with `pg_upgrade` or logical replication; cross-version on-disk format isn't compatible.

## Hosting

The popular managed options:

- **AWS RDS / Aurora Postgres** — easy, expensive at scale.
- **Google Cloud SQL** / **Azure Database for PostgreSQL**.
- **Crunchy Bridge**, **Neon**, **Supabase**, **PlanetScale Postgres**, **DigitalOcean Managed**.

For learning, install locally or run `docker run -e POSTGRES_PASSWORD=secret -p 5432:5432 postgres:16`.
