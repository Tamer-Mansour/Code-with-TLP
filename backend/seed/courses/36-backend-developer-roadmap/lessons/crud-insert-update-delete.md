# CRUD: INSERT, UPDATE, DELETE

You already know how to retrieve rows with `SELECT`. The remaining three write operations — **INSERT**, **UPDATE**, and **DELETE** — are what turn a database into a live, mutable store of application data. Together with `SELECT` they form the four CRUD operations every backend developer uses daily.

## The Sample Table

All examples below assume this table, which you created in the previous lesson:

```sql
CREATE TABLE employees (
    id         INT          AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    department VARCHAR(50)  NOT NULL,
    salary     DECIMAL(10, 2) NOT NULL,
    hired_on   DATE         NOT NULL
);
```

## INSERT — Adding Rows

### Single-row insert

```sql
INSERT INTO employees (name, department, salary, hired_on)
VALUES ('Sara Ali', 'Engineering', 72000.00, '2024-03-15');
```

You do not include `id` because `AUTO_INCREMENT` generates it automatically.

### Multi-row insert (one statement, much faster)

```sql
INSERT INTO employees (name, department, salary, hired_on)
VALUES
    ('Omar Hassan', 'Marketing',   58000.00, '2024-04-01'),
    ('Lina Nour',   'Engineering', 81000.00, '2023-11-20'),
    ('Karim Fathi', 'HR',          50000.00, '2024-01-10');
```

Batching rows in a single `INSERT` reduces round-trips to the server and is the preferred approach when seeding or importing data.

## UPDATE — Modifying Existing Rows

```sql
UPDATE employees
SET    salary     = 76000.00,
       department = 'Engineering'
WHERE  id = 1;
```

`SET` accepts a comma-separated list of column assignments. The `WHERE` clause filters which rows are changed.

### Relative updates

You can use the current column value in the expression:

```sql
-- Give the Engineering department a 10 % raise
UPDATE employees
SET   salary = salary * 1.10
WHERE department = 'Engineering';
```

| Clause | Required? | Effect if omitted |
|--------|-----------|-------------------|
| `WHERE` | No | **Every row** in the table is updated |
| `SET`   | Yes | Statement is a syntax error |

Always supply a `WHERE` clause unless you genuinely intend to touch every row.

## DELETE — Removing Rows

```sql
-- Remove one specific employee
DELETE FROM employees
WHERE id = 4;

-- Remove all HR staff (multiple rows)
DELETE FROM employees
WHERE department = 'HR';
```

Like `UPDATE`, omitting `WHERE` deletes **all rows** in the table (the table structure remains; only the data is gone). If you want to erase all rows and reset the `AUTO_INCREMENT` counter, use `TRUNCATE TABLE employees;` instead.

## Dry-Run Pattern: SELECT Before You Write

Before running a destructive `UPDATE` or `DELETE`, rewrite it as a `SELECT` first to verify the target rows:

```sql
-- Step 1: confirm what will be affected
SELECT id, name, department
FROM   employees
WHERE  department = 'HR';

-- Step 2: once confirmed, run the write
DELETE FROM employees
WHERE department = 'HR';
```

This habit prevents accidental data loss that a `WHERE` typo could cause.

## Using Transactions for Safety

Wrap related writes in a transaction so you can roll back if anything goes wrong:

```sql
START TRANSACTION;

UPDATE employees SET salary = 90000.00 WHERE id = 2;
DELETE FROM employees WHERE id = 5;

-- Inspect the result before committing
SELECT * FROM employees WHERE id IN (2, 5);

COMMIT;   -- make it permanent
-- or ROLLBACK; to undo both statements
```

`COMMIT` makes all changes visible to other connections. `ROLLBACK` undoes every statement since `START TRANSACTION`.

## Common Mistakes to Avoid

- **Missing `WHERE` on UPDATE / DELETE.** The query is still valid SQL and will silently mutate or erase every row.
- **Inserting a duplicate primary key.** Use `INSERT IGNORE` or `INSERT … ON DUPLICATE KEY UPDATE` when the row might already exist.
- **Inserting `NULL` into a `NOT NULL` column.** MySQL raises an error; always supply a value or define a `DEFAULT`.
- **Skipping transactions for multi-step writes.** If two related statements must both succeed or both fail, wrap them in `START TRANSACTION … COMMIT`.
- **Forgetting `AUTO_INCREMENT` gaps.** A rolled-back `INSERT` still consumes an ID. Do not treat sequential IDs as meaningful business data.

---

`INSERT`, `UPDATE`, and `DELETE` are the write half of SQL; master the `WHERE` clause and transaction boundaries and you can safely manage any relational dataset your Spring application needs.
