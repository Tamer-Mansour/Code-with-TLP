# Exercise: Transaction Isolation — Detect Phantom Reads

Reinforce your understanding of PostgreSQL transaction isolation levels by identifying phantom read anomalies in a transaction log.

## Background

PostgreSQL's default isolation level is `READ COMMITTED` — not `SERIALIZABLE`. This is a common misconception: many developers assume Postgres is fully serializable by default, but `READ COMMITTED` allows certain read anomalies.

**Isolation anomalies explained:**

| Anomaly | Description | First prevented at |
|---|---|---|
| Dirty read | Reading uncommitted data from another transaction | READ COMMITTED |
| Non-repeatable read | Same row returns different values in the same transaction | REPEATABLE READ |
| Phantom read | A range query returns new rows on re-execution within a transaction | REPEATABLE READ (in Postgres) |
| Write skew | Two transactions read overlapping data and write based on stale reads | SERIALIZABLE |

PostgreSQL prevents dirty reads at all levels (even `READ UNCOMMITTED` behaves like `READ COMMITTED`). Phantom reads are prevented at `REPEATABLE READ` in Postgres — stricter than the SQL standard which only prevents them at `SERIALIZABLE`.

## Example Scenario

```sql
-- Transaction A starts at READ COMMITTED (default)
BEGIN;
SELECT COUNT(*) FROM orders WHERE amount > 100;  -- returns 5

-- Meanwhile, Transaction B inserts and commits:
INSERT INTO orders (amount) VALUES (150);
COMMIT;

-- Transaction A re-queries:
SELECT COUNT(*) FROM orders WHERE amount > 100;  -- now returns 6 (phantom!)
COMMIT;
```

To prevent this:

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- now both SELECTs see the same snapshot
```

## Setting Isolation Level

```sql
-- Per transaction:
BEGIN ISOLATION LEVEL SERIALIZABLE;

-- Per session:
SET default_transaction_isolation = 'repeatable read';

-- In application code (psycopg2):
conn.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
```

## Serializable Snapshot Isolation (SSI)

PostgreSQL's `SERIALIZABLE` level uses SSI — it tracks read-write dependencies between transactions and aborts one if a dangerous anti-dependency cycle is detected at commit time. This is much more efficient than traditional lock-based serialization.

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- do reads and writes
COMMIT;  -- may raise: ERROR: could not serialize access due to read/write dependencies
```

Your application must catch `serialization_failure` (SQLSTATE 40001) and retry the transaction.

## Reference

- [PostgreSQL Official Documentation — Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [PostgreSQL Tutorial — Transaction Isolation Levels](https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-transaction/)
- [PostgreSQL Notes for Professionals](https://books.goalkicker.com/PostgreSQLBook/) — Chapter on transactions and concurrency

## Your Task

Parse the event log and identify which transactions experienced a phantom read (new rows appeared in their second READ that were absent in their first READ). See the prompt for the full specification.
