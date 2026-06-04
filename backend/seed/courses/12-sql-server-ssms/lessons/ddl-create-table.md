# DDL: Creating Tables and Choosing Data Types

Data Definition Language (DDL) is the subset of SQL that defines the **structure** of your database — schemas, tables, columns, and constraints. Getting DDL right up front saves painful migrations later.

## CREATE TABLE

```sql
CREATE TABLE dbo.products (
    product_id   INT           NOT NULL IDENTITY(1,1),
    sku          VARCHAR(50)   NOT NULL,
    name         NVARCHAR(200) NOT NULL,
    price        DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    is_active    BIT           NOT NULL DEFAULT 1,
    created_at   DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT pk_products PRIMARY KEY (product_id),
    CONSTRAINT uq_products_sku UNIQUE (sku),
    CONSTRAINT ck_products_price CHECK (price >= 0)
);
```

## Choosing the Right Data Type

Choosing a precise data type matters for storage, performance, and correctness.

| Use Case | Recommended Type | Avoid |
|----------|-----------------|-------|
| Integer surrogate key | `INT` or `BIGINT` | `FLOAT` |
| Short ASCII text (emails, codes) | `VARCHAR(n)` | `TEXT` |
| Unicode text (names, content) | `NVARCHAR(n)` | `NTEXT` |
| Money / exact decimal | `DECIMAL(p,s)` | `FLOAT`, `MONEY` |
| Boolean flag | `BIT` | `CHAR(1)` |
| Date + time (UTC) | `DATETIME2` | `DATETIME` (less precision) |
| Date only | `DATE` | `DATETIME2` |
| Large binary (files) | `VARBINARY(MAX)` | Storing files in the DB at all |

`NVARCHAR` stores Unicode (2 bytes per character). If you only store ASCII/Latin-1 and every byte of storage matters, use `VARCHAR`. For most modern applications, default to `NVARCHAR`.

## Constraints

Constraints enforce **data integrity at the database level** — no matter which application writes to the table.

### PRIMARY KEY

```sql
CONSTRAINT pk_orders PRIMARY KEY (order_id)
```

Uniquely identifies each row. Implicitly NOT NULL. By default becomes the **clustered index**.

### FOREIGN KEY

```sql
CONSTRAINT fk_order_items_order
    FOREIGN KEY (order_id) REFERENCES dbo.orders(order_id)
    ON DELETE CASCADE
```

Enforces referential integrity. `ON DELETE CASCADE` propagates deletes. `ON DELETE NO ACTION` (default) blocks the delete if child rows exist.

### UNIQUE

```sql
CONSTRAINT uq_users_email UNIQUE (email)
```

No duplicate values allowed in the column. NULLs are allowed (multiple NULLs don't conflict in SQL Server).

### CHECK

```sql
CONSTRAINT ck_employees_age CHECK (age BETWEEN 16 AND 120)
CONSTRAINT ck_orders_status  CHECK (status IN ('pending','paid','cancelled'))
```

Enforces a domain rule on insert and update. Violations raise an error.

### DEFAULT

```sql
created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
```

Supplies a value when the INSERT omits the column.

## IDENTITY Column

```sql
product_id INT NOT NULL IDENTITY(1,1)
```

SQL Server auto-generates the value — starting at 1, incrementing by 1. You cannot insert into an `IDENTITY` column directly unless you use `SET IDENTITY_INSERT dbo.products ON`.

## ALTER TABLE

You can modify a table after creation:

```sql
-- Add a column
ALTER TABLE dbo.products ADD weight_kg DECIMAL(8,3) NULL;

-- Add a constraint
ALTER TABLE dbo.products
ADD CONSTRAINT ck_products_weight CHECK (weight_kg >= 0);

-- Drop a column (must drop constraints referencing it first)
ALTER TABLE dbo.products DROP COLUMN weight_kg;
```

## DROP TABLE

```sql
DROP TABLE IF EXISTS dbo.products;
```

`IF EXISTS` prevents an error if the table is already gone. Be careful: this is irreversible without a backup.

> **Further reading:** *Database Design — 2nd Edition* by Adrienne Watt (BCcampus, free) covers data types, constraints, and ER-to-table translation in depth — https://opentextbc.ca/dbdesign01/
