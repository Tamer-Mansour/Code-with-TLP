# Locking and Deadlocks in PostgreSQL

Postgres uses a layered locking system: table-level locks for DDL and bulk operations, row-level locks for concurrent DML. Understanding the lock hierarchy prevents the two most common production surprises: unexpected lock waits and deadlocks.

## Table-level lock modes

| Lock mode              | Acquired by                          | Conflicts with                   |
|------------------------|--------------------------------------|----------------------------------|
| `ACCESS SHARE`         | `SELECT`                             | `ACCESS EXCLUSIVE` only          |
| `ROW SHARE`            | `SELECT FOR UPDATE/SHARE`            | `EXCLUSIVE`, `ACCESS EXCLUSIVE`  |
| `ROW EXCLUSIVE`        | `INSERT`, `UPDATE`, `DELETE`         | `SHARE` and above                |
| `SHARE UPDATE EXCLUSIVE` | `VACUUM`, `ANALYZE`, some `ALTER` | itself and stronger              |
| `SHARE`                | `CREATE INDEX` (non-concurrent)      | writes                           |
| `EXCLUSIVE`            | Rare; explicit `LOCK TABLE ... EXCLUSIVE` | reads and writes          |
| `ACCESS EXCLUSIVE`     | `DROP TABLE`, `TRUNCATE`, many `ALTER TABLE` | everything           |

The key insight: an `ALTER TABLE` that takes `ACCESS EXCLUSIVE` blocks **all** reads and writes. This is why long-running migrations on busy tables cause outages.

## Row-level locks

Row locks are taken within a transaction and released at commit:

```sql
-- Lock rows for update (other sessions block on the same rows)
SELECT id, balance FROM accounts WHERE id = 42 FOR UPDATE;

-- Skip locked rows — useful for job queues
SELECT id FROM tasks WHERE status = 'pending' LIMIT 1 FOR UPDATE SKIP LOCKED;

-- Read-compatible share lock
SELECT * FROM orders WHERE id = 7 FOR SHARE;
```

`SKIP LOCKED` is the standard pattern for building a queue consumer: each worker grabs a different row rather than queuing up behind the first worker.

## Seeing current locks

```sql
SELECT pid, relation::regclass, mode, granted, query
FROM pg_locks l
JOIN pg_stat_activity a USING (pid)
WHERE relation IS NOT NULL
ORDER BY granted, relation;
```

`granted = false` means the session is **waiting** for the lock. The session holding the blocking lock appears with `granted = true` on the same relation.

## Deadlocks

A deadlock occurs when two transactions each hold a lock the other needs:

```
Txn A: holds lock on row 1, wants row 2
Txn B: holds lock on row 2, wants row 1
```

Postgres detects this within `deadlock_timeout` (default 1 second) and kills one transaction with:

```
ERROR:  deadlock detected
DETAIL:  Process 12345 waits for ShareLock on transaction 67890;
         blocked by process 99999.
```

**Prevention strategies:**

1. **Always lock resources in the same order.** If all code locks `accounts` rows in ascending `id` order, cycles cannot form.
2. **Keep transactions short.** Fewer concurrent lock holders means fewer chances to interlock.
3. **Use `SELECT ... FOR UPDATE NOWAIT`** to fail fast rather than waiting — surface contention early in testing.
4. **Batch DML carefully.** Updating rows in random order inside a single transaction is a deadlock recipe.

## Advisory locks

For application-level mutual exclusion that doesn't correspond to a table row:

```sql
-- Session-level: released when the connection closes
SELECT pg_try_advisory_lock(12345);   -- non-blocking, returns bool
SELECT pg_advisory_unlock(12345);

-- Transaction-level: released at COMMIT/ROLLBACK
SELECT pg_try_advisory_xact_lock(12345);
```

Advisory locks are cheap and flexible — useful for leader election or "only one worker processes this job" patterns where you don't want to put a sentinel row in a table.

## Safe zero-downtime ALTER TABLE

Avoid `ACCESS EXCLUSIVE` on live tables by using concurrent-safe patterns:

- Add a nullable column: no rewrite, takes only a brief lock.
- Use `CREATE INDEX CONCURRENTLY` instead of plain `CREATE INDEX`.
- For NOT NULL constraints, add the constraint as `NOT VALID`, backfill, then `VALIDATE CONSTRAINT` (which only takes `SHARE UPDATE EXCLUSIVE`).
