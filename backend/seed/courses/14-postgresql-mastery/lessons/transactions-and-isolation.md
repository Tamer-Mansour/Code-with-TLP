# Transactions and Isolation Levels

Postgres transactions are ACID like the others, with two specifics worth knowing: the **isolation levels** behave a bit differently from SQL Server / Oracle, and you can use **serializable** in production without it being slow.

## Basic syntax

```sql
BEGIN;
UPDATE accounts SET balance = balance - 10 WHERE id = 1;
UPDATE accounts SET balance = balance + 10 WHERE id = 2;
COMMIT;
-- ROLLBACK; to undo
```

Inside `psql`, `BEGIN` and `START TRANSACTION` are identical.

## Isolation levels

| Level                | Reads see             | Anomalies prevented              |
|----------------------|-----------------------|----------------------------------|
| READ UNCOMMITTED *   | Like READ COMMITTED   | (Postgres has no dirty reads ever) |
| READ COMMITTED (default) | Each query's own snapshot | Dirty reads                    |
| REPEATABLE READ      | One snapshot for the whole tx | + non-repeatable, + phantoms |
| SERIALIZABLE         | Snapshot + SSI conflict detection | + write skew, full serializability |

\* Postgres treats `READ UNCOMMITTED` as `READ COMMITTED`. There's no actual "dirty read" mode.

Set per session or per transaction:

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

## READ COMMITTED — the default

Every individual statement sees a consistent snapshot — but consecutive statements in the same transaction may see different snapshots, so a re-read can return a different value.

```sql
BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- 100
-- (another transaction updates and commits)
SELECT balance FROM accounts WHERE id = 1;  -- 90  ← non-repeatable read
COMMIT;
```

## REPEATABLE READ

Single snapshot for the whole transaction. Postgres throws **`could not serialize access due to concurrent update`** if two transactions try to update the same row — your code must retry.

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- everything you read is from the moment BEGIN ran
COMMIT;
```

## SERIALIZABLE

The strongest level. Postgres's implementation is **Serializable Snapshot Isolation (SSI)** — it detects dangerous read-write conflict patterns at commit time and aborts one transaction. It's surprisingly efficient.

Use for code where you read state and write based on it, where lost updates would be a real bug (banking, inventory, booking).

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- do reads and writes
COMMIT;  -- may raise serialization_failure
```

Your application **must** handle the serialization failure and retry. Wrap in a loop with backoff.

## SELECT FOR UPDATE / FOR SHARE / SKIP LOCKED

When you want explicit row locking:

```sql
-- Lock for write
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;

-- Lock and skip rows another tx has locked (great for queues)
SELECT id FROM jobs WHERE status = 'queued' ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED;
```

`FOR UPDATE SKIP LOCKED` is the modern way to build a database-backed work queue without deadlocks.

## Advisory locks

Application-defined locks Postgres holds for you:

```sql
SELECT pg_advisory_lock(42);
-- only one connection at a time gets this lock
SELECT pg_advisory_unlock(42);
```

Useful for cross-connection mutual exclusion (e.g., "only one cron job at a time").

## Deadlocks

Two transactions can each hold a lock the other wants. Postgres detects it and aborts the loser with `deadlock_detected`. Application must retry. Minimize by:

- Acquiring locks in a consistent order.
- Keeping transactions short.
- Avoiding `SELECT FOR UPDATE` followed by long application work.
