# ACID and Isolation Levels

A **transaction** is a unit of work that succeeds entirely or fails entirely. MySQL's InnoDB engine gives you four properties known as **ACID**.

## ACID

- **Atomic** — all statements commit, or none do.
- **Consistent** — constraints (FKs, CHECKs) hold before and after.
- **Isolated** — concurrent transactions don't see each other's partial work.
- **Durable** — once committed, the change survives a crash.

## Basic syntax

```sql
START TRANSACTION;
UPDATE accounts SET balance = balance - 10 WHERE id = 1;
UPDATE accounts SET balance = balance + 10 WHERE id = 2;
COMMIT;
-- or ROLLBACK;
```

If anything fails between `START` and `COMMIT`, `ROLLBACK` returns the database to its pre-transaction state.

## Isolation levels

The SQL standard defines four levels, trading **isolation strictness** against **concurrency**.

| Level                | Dirty read | Non-repeatable read | Phantom read |
|----------------------|:----------:|:-------------------:|:------------:|
| READ UNCOMMITTED     | ✓          | ✓                   | ✓            |
| READ COMMITTED       | ✗          | ✓                   | ✓            |
| **REPEATABLE READ**  | ✗          | ✗                   | ✓ (✗ in InnoDB) |
| SERIALIZABLE         | ✗          | ✗                   | ✗            |

- **Dirty read** — reading another transaction's uncommitted change.
- **Non-repeatable read** — same query, different answer within one transaction.
- **Phantom read** — same range query, new rows appear within one transaction.

**InnoDB's default is `REPEATABLE READ`**, and thanks to MVCC + next-key locks it also prevents phantom reads in practice.

Set it per session:

```sql
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

## MVCC in one paragraph

InnoDB keeps multiple versions of each row. A reader gets a snapshot as of transaction start; writers create new versions, leaving old ones visible to in-flight readers. That's why `SELECT` doesn't block `INSERT`/`UPDATE` and vice versa — they each see a consistent view.

## Locks

Some operations grab locks:

- `SELECT ... FOR UPDATE` — exclusive lock on read rows.
- `SELECT ... FOR SHARE` — shared (read) lock.
- Any `UPDATE`/`DELETE` — implicit X-lock on affected rows + their gap locks.

Use `FOR UPDATE` when you read a value, decide based on it, and write back:

```sql
START TRANSACTION;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
-- balance is now safe to read; another tx can't change it until we commit
UPDATE accounts SET balance = balance - 10 WHERE id = 1;
COMMIT;
```

Without `FOR UPDATE`, two concurrent withdrawals could both read $100, both subtract, and both write $90 — a lost update.

## Deadlocks

Two transactions can each hold a lock the other wants. InnoDB detects this and **kills one of them** with error 1213. Your application should catch that and retry. Keep transactions short and access tables in a consistent order to minimize deadlocks.

## Autocommit

Each `SELECT/INSERT/UPDATE/DELETE` is its own transaction unless you started one. Toggle:

```sql
SET autocommit = 0;       -- now you must COMMIT or ROLLBACK explicitly
```

Most application frameworks already manage transactions for you (`@Transactional`, `db.transaction(...)`, etc.).
