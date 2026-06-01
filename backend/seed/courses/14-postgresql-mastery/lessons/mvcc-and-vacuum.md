# MVCC and VACUUM

Postgres uses **MVCC** — Multi-Version Concurrency Control. It's how readers don't block writers and vice versa, and it explains why Postgres needs `VACUUM`.

## How MVCC works

When you `UPDATE` a row, Postgres doesn't overwrite it. It:

1. Marks the existing row version with `xmax = current_xid` (this row is dead to transactions newer than xid).
2. Inserts a new row version with `xmin = current_xid` (alive starting from xid).

Each row has hidden columns `xmin` (the xid that created it) and `xmax` (the xid that deleted/replaced it). A row is **visible** to your transaction if `xmin` is committed and ≤ your snapshot xid, and `xmax` is either NULL, not committed, or > your snapshot xid.

`DELETE` is the same minus the new row.

So every UPDATE/DELETE produces **dead tuples** — old versions that are invisible but still on disk.

## Why VACUUM exists

Dead tuples accumulate. They take space, slow down scans, and (worst of all) get in the way of `xid` wraparound recycling. `VACUUM` reclaims them.

There are two flavors:

- **`VACUUM`** — marks dead tuples reusable. Doesn't return disk to the OS. Non-blocking.
- **`VACUUM FULL`** — rewrites the table compactly. Returns disk. **Takes an exclusive lock** — never on production tables.

## Autovacuum

A background worker runs `VACUUM` automatically when tables exceed thresholds. Tunables:

```sql
ALTER TABLE big_table SET (
  autovacuum_vacuum_scale_factor = 0.05,    -- vacuum when 5% dead (default 20%)
  autovacuum_vacuum_cost_limit   = 2000
);
```

Look at `pg_stat_user_tables` to see when each table was last vacuumed:

```sql
SELECT relname, last_vacuum, last_autovacuum, n_dead_tup
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC LIMIT 20;
```

## ANALYZE

`ANALYZE` (also run by autovacuum) updates **planner statistics** — histograms of column values used to estimate row counts.

If queries get suddenly slow, especially after big imports, run `ANALYZE` first.

## Bloat

A bloated table has lots of dead tuples + reusable space. Symptoms:

- Disk usage growing faster than data.
- `pg_stat_user_tables.n_dead_tup` enormous compared to `n_live_tup`.

Use `pgstattuple` (an extension) for hard numbers:

```sql
CREATE EXTENSION pgstattuple;
SELECT * FROM pgstattuple('big_table');
```

Fix mild bloat with autovacuum tuning. Severe bloat needs `pg_repack` (online table rewriter, doesn't lock) or, on small tables, `VACUUM FULL`.

## XID wraparound

`xid`s are 32 bits. Around ~2 billion transactions Postgres needs to "freeze" old rows by clearing their xmin/xmax to a special "frozen" marker — otherwise the xid counter wraps and old rows look like the future.

Autovacuum handles freezing. If autovacuum falls behind on huge tables, you hit the dreaded **xid wraparound emergency** — Postgres refuses writes until you VACUUM. Monitor `age(datfrozenxid)`:

```sql
SELECT datname, age(datfrozenxid)
FROM pg_database
ORDER BY age(datfrozenxid) DESC;
```

If age is creeping toward 200 million, your autovacuum is failing. Fix it before you hit 1.5 billion.

## VACUUM is not optional

A "set-and-forget" mindset works for years on small databases. At scale you'll watch autovacuum settings the same way you watch disk usage. Read your `last_autovacuum` numbers periodically.
