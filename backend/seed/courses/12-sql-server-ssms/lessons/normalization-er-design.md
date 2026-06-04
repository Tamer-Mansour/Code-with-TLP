# Database Normalization and ER Design

A well-normalized schema eliminates redundancy, prevents update anomalies, and keeps data consistent. Understanding the first three normal forms is essential for any SQL Server developer.

## Why Normalize?

Consider a single denormalized table:

| order_id | customer_name | customer_email | product_name | qty | price |
|----------|--------------|----------------|-------------|-----|-------|
| 1 | Alice | alice@x.com | Widget | 2 | 9.99 |
| 2 | Alice | alice@x.com | Gadget | 1 | 24.99 |
| 3 | Bob | bob@y.com | Widget | 5 | 9.99 |

Problems:
- Alice's email is stored in every order — changing it requires updating multiple rows.
- If you delete order 3, you lose Bob's contact information entirely.
- Widget's price is repeated; if it changes, you must update every row.

## First Normal Form (1NF)

**Rule:** Each cell contains a single, atomic value. No repeating groups.

**Violation:**
```
order_id=1, products='Widget, Gadget'   -- multi-valued cell
```

**Fix:** One product per row. Each row represents one fact.

## Second Normal Form (2NF)

**Rule:** 1NF, and every non-key column is **fully functionally dependent** on the entire primary key (no partial dependencies).

Applies when the primary key is composite. If `customer_name` depends only on `customer_id` (not on `order_id`), it belongs in a separate `customers` table.

## Third Normal Form (3NF)

**Rule:** 2NF, and no transitive dependencies — non-key columns depend only on the primary key, not on other non-key columns.

**Example violation:** `zip_code → city` — if both `zip_code` and `city` are in the `customers` table and city depends on zip_code (not directly on customer_id), that's a transitive dependency. Extract `zip_codes(zip_code, city)`.

## Normalized Schema Example

```sql
CREATE TABLE dbo.customers (
    customer_id INT NOT NULL IDENTITY(1,1),
    name        NVARCHAR(100) NOT NULL,
    email       VARCHAR(200)  NOT NULL,
    CONSTRAINT pk_customers PRIMARY KEY (customer_id),
    CONSTRAINT uq_customers_email UNIQUE (email)
);

CREATE TABLE dbo.products (
    product_id  INT NOT NULL IDENTITY(1,1),
    name        NVARCHAR(200) NOT NULL,
    price       DECIMAL(10,2) NOT NULL,
    CONSTRAINT pk_products PRIMARY KEY (product_id)
);

CREATE TABLE dbo.orders (
    order_id    INT NOT NULL IDENTITY(1,1),
    customer_id INT NOT NULL,
    ordered_at  DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT pk_orders PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
        REFERENCES dbo.customers(customer_id)
);

CREATE TABLE dbo.order_items (
    order_id   INT NOT NULL,
    product_id INT NOT NULL,
    qty        INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,   -- snapshot price at time of order
    CONSTRAINT pk_order_items PRIMARY KEY (order_id, product_id),
    CONSTRAINT fk_oi_order   FOREIGN KEY (order_id)   REFERENCES dbo.orders(order_id),
    CONSTRAINT fk_oi_product FOREIGN KEY (product_id) REFERENCES dbo.products(product_id)
);
```

## Entity-Relationship (ER) Diagrams

An ER diagram maps the real world to tables before you write a single line of SQL.

Key symbols:
- **Rectangle** — entity (becomes a table)
- **Oval** — attribute (becomes a column)
- **Diamond** — relationship (becomes a foreign key or junction table)
- **Double rectangle** — weak entity (depends on a parent for its identity)

Cardinality notation:
- `1:1` — one customer has one passport
- `1:N` — one customer has many orders
- `M:N` — many orders can contain many products (requires a junction table: `order_items`)

## Translating ER to Tables

1. Each entity becomes a table with a surrogate `INT IDENTITY` primary key.
2. Each 1:N relationship becomes a foreign key column on the "many" side.
3. Each M:N relationship becomes a **junction table** with a composite primary key made up of both foreign keys.
4. Attributes become columns with the most restrictive appropriate data type.

> **Further reading:** *Database Design — 2nd Edition* by Adrienne Watt and Nelson Eng (BCcampus) is a free open textbook covering ER modeling, 1NF through 3NF, and normalization exercises with solutions — https://opentextbc.ca/dbdesign01/
