# Keys, Constraints, and Normalization

A good schema makes invalid states impossible to represent. MySQL gives you four tools.

## Primary keys

Every table should have one. It uniquely identifies a row.

```sql
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  ...
);
```

In InnoDB the primary key is also the **clustered index** — rows are physically stored in PK order. Pick a small, monotonically increasing PK (e.g., `BIGINT AUTO_INCREMENT` or `BINARY(16)` UUIDv7) for the best write throughput.

Random UUIDv4 PKs are convenient but trash the buffer pool — every insert lands in a different page.

## Foreign keys

```sql
CREATE TABLE orders (
  id      INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  amount  INT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE RESTRICT ON UPDATE CASCADE
);
```

`ON DELETE` options: `RESTRICT` (block), `CASCADE` (delete children), `SET NULL` (null the column).

Foreign keys cost a small amount of write performance, but they keep your data honest. Use them.

## UNIQUE constraints

```sql
CREATE TABLE users (
  id    INT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(200) NOT NULL,
  UNIQUE KEY (email)
);
```

`UNIQUE` is enforced by an index — bonus: that column is now efficiently queryable by equality.

## CHECK constraints

MySQL 8 enforces them:

```sql
CREATE TABLE products (
  id    INT PRIMARY KEY,
  price DECIMAL(10,2) NOT NULL CHECK (price >= 0)
);
```

## Normalization (briefly)

Normal forms are rules for splitting data so each fact lives in exactly one place:

- **1NF** — every cell holds one value (no comma-lists in a column).
- **2NF** — every non-key column depends on the *whole* primary key.
- **3NF** — every non-key column depends on the key, the whole key, and *nothing but the key*.

In practice, aim for **3NF as a default**, then *denormalize* deliberately when read patterns demand it (e.g., precomputed counters). Premature denormalization is the source of most data-integrity bugs you'll see in your career.

## A normalized example

Bad:

```
orders(id, user_email, user_name, product_csv, total)
```

`user_email` and `user_name` are facts about the user, not the order. `product_csv` is a list jammed into a string.

Good:

```
users(id, email, name)
orders(id, user_id, total)
order_items(order_id, product_id, quantity, price)
products(id, name)
```

Each fact in one place; relationships expressed by IDs.

## Index naming convention

```sql
CREATE INDEX ix_orders_user_id        ON orders(user_id);
CREATE UNIQUE INDEX uq_users_email    ON users(email);
```

Consistent prefixes (`ix_`, `uq_`, `pk_`, `fk_`) make `SHOW INDEX` readable at a glance.
