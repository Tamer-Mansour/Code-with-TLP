# DML: INSERT, UPDATE, DELETE, and Safe Mutation

Data Manipulation Language (DML) is the set of statements that add, modify, and remove rows. Getting DML wrong can silently corrupt production data — this lesson focuses on safe patterns.

## INSERT

### Single-row INSERT

```sql
INSERT INTO dbo.customers (name, email)
VALUES ('Alice', 'alice@example.com');
```

Always list the column names explicitly. Relying on column order breaks when someone runs `ALTER TABLE ADD COLUMN`.

### Multi-row INSERT

```sql
INSERT INTO dbo.products (name, price)
VALUES
    ('Widget', 9.99),
    ('Gadget', 24.99),
    ('Doohickey', 4.50);
```

SQL Server processes multi-row inserts as a single statement — faster than N separate inserts.

### INSERT ... SELECT

```sql
INSERT INTO dbo.orders_archive (order_id, customer_id, total, archived_at)
SELECT order_id, customer_id, total, SYSUTCDATETIME()
FROM   dbo.orders
WHERE  created_at < DATEADD(year, -2, GETDATE());
```

## UPDATE

```sql
UPDATE dbo.products
SET    price = price * 1.05,     -- 5% price increase
       updated_at = SYSUTCDATETIME()
WHERE  category_id = 3;
```

### CRITICAL: Always use WHERE with UPDATE

An `UPDATE` without a `WHERE` clause modifies **every row in the table**:

```sql
-- DANGEROUS — updates ALL employees:
UPDATE dbo.employees SET salary = 0;

-- Safe — targets one employee:
UPDATE dbo.employees SET salary = 0 WHERE employee_id = 42;
```

A practical safety habit: run a `SELECT` with the same `WHERE` clause first to confirm how many rows you are about to change.

## DELETE

```sql
DELETE FROM dbo.audit_log
WHERE created_at < DATEADD(month, -6, GETDATE());
```

### DELETE vs TRUNCATE TABLE

These are **not equivalent**:

| Feature | DELETE | TRUNCATE TABLE |
|---------|--------|---------------|
| Can use WHERE | Yes | No — removes all rows |
| Logged | Fully (row-by-row) | Minimally (page deallocation) |
| Fires triggers | Yes | No |
| Resets IDENTITY | No | Yes |
| Foreign key blocked | No | Yes (if FK exists) |
| Can roll back | Yes | Yes if inside explicit transaction |

Use `TRUNCATE` only when you intentionally want to empty an entire table fast and there are no foreign key constraints pointing to it.

## Transactions

Wrap related DML statements so they all succeed or all roll back:

```sql
BEGIN TRANSACTION;

UPDATE dbo.accounts SET balance = balance - 500 WHERE account_id = 1;
UPDATE dbo.accounts SET balance = balance + 500 WHERE account_id = 2;

-- Check: did both rows update?
IF @@ROWCOUNT <> 1
BEGIN
    ROLLBACK TRANSACTION;
    THROW 50001, 'Unexpected row count during transfer', 1;
END

COMMIT TRANSACTION;
```

## ACID Properties

SQL Server transactions guarantee ACID:

- **Atomicity** — all-or-nothing. Either every statement in the transaction succeeds, or none of their effects persist.
- **Consistency** — constraints are checked. A transaction that would violate a CHECK or FK constraint is rolled back.
- **Isolation** — concurrent transactions see a consistent snapshot of data (isolation level controls how much they can see of each other's in-progress work).
- **Durability** — once committed, changes survive restarts. The transaction log is written to disk before the commit is acknowledged.

> **Key insight:** The default isolation level in SQL Server is `READ COMMITTED` — not `SERIALIZABLE`. This means concurrent sessions can see committed changes from each other mid-transaction, making non-repeatable reads possible. Wrapping your statements in `BEGIN TRAN / COMMIT` does **not** prevent all concurrency anomalies — the isolation level determines what is possible.

> **Further reading:** *Microsoft SQL Server Notes for Professionals* (GoalKicker) covers INSERT, MERGE, transactions, and isolation levels — free at https://books.goalkicker.com/MicrosoftSQLServerBook/
