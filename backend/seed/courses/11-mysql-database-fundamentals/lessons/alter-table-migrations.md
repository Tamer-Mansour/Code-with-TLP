# ALTER TABLE and Schema Migrations

Real databases evolve over time. The `ALTER TABLE` statement lets you change a table's structure after it has been created — adding columns, changing types, dropping constraints, and renaming things — without recreating the table from scratch.

## Common ALTER TABLE operations

```sql
-- Add a new nullable column
ALTER TABLE users ADD COLUMN bio TEXT;

-- Add a column with a default value
ALTER TABLE orders ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending';

-- Change a column's data type
ALTER TABLE products MODIFY COLUMN price DECIMAL(12, 2) NOT NULL;

-- Rename a column (MySQL 8.0+)
ALTER TABLE users RENAME COLUMN username TO handle;

-- Drop a column
ALTER TABLE sessions DROP COLUMN legacy_token;

-- Add a foreign key constraint
ALTER TABLE orders
  ADD CONSTRAINT fk_orders_user
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Drop a constraint
ALTER TABLE orders DROP FOREIGN KEY fk_orders_user;
```

## Online DDL vs locking DDL

Older MySQL versions locked the whole table during `ALTER TABLE`, blocking all reads and writes for the duration. InnoDB's **Online DDL** (introduced in MySQL 5.6 and improved in 8.0) lets many operations run while the table stays readable and writable.

| Operation | Online? | Notes |
|---|:---:|---|
| Add/drop column | Yes (most cases) | Rebuilds table in background |
| Add index | Yes | Index built without table lock |
| Change column type | No | Full lock required |
| Rename column | Yes | Metadata change only |
| Add FK | Yes | Validates existing data first |

For large tables in production, use **pt-online-schema-change** (from Percona Toolkit) or **gh-ost** (GitHub's tool) instead of plain `ALTER TABLE`. They copy data in the background with minimal downtime.

## Schema migration workflows

Never run raw `ALTER TABLE` scripts by hand in production. Use a migration framework:

- **Flyway** – versioned SQL scripts (`V1__add_bio.sql`), works with any language.
- **Liquibase** – XML/YAML/SQL changelogs, rollback support.
- **Django / Laravel / Rails migrations** – ORM-generated migrations tied to your model layer.

A typical migration file in Flyway:

```sql
-- V5__add_status_to_orders.sql
ALTER TABLE orders
  ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending';

CREATE INDEX ix_orders_status ON orders(status);
```

The framework tracks which scripts have run in a `flyway_schema_history` table, so the same migration never executes twice.

## Safety checklist before migrating production

1. **Take a backup** (or verify Point-In-Time Recovery is set up).
2. Test the migration on a staging database first.
3. Check `INFORMATION_SCHEMA.INNODB_TRX` — long-running transactions will block your `ALTER`.
4. Run during low-traffic hours if the operation isn't truly online.
5. Have a rollback script ready (`DROP COLUMN`, `DROP INDEX`, etc.).

## Inspecting the current schema

```sql
DESCRIBE users;

-- or more detail:
SHOW CREATE TABLE orders\G
```

`SHOW CREATE TABLE` gives you the exact DDL including all constraints and options — useful before you write an `ALTER`.
