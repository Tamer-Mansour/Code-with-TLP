# Exercise: Simulate an INNER JOIN

The JOIN operation is the most fundamental multi-table operation in relational databases. It combines rows from two tables based on a related column — in this case, a foreign key relationship.

## The SQL Equivalent

```sql
SELECT o.order_id, c.customer_name
FROM   dbo.orders    AS o
INNER JOIN dbo.customers AS c ON o.customer_id = c.customer_id
ORDER BY o.order_id;
```

An `INNER JOIN` returns **only rows with a matching value in both tables**. Orders whose `customer_id` has no corresponding customer are excluded. Customers with no orders are also excluded.

## Why INNER JOIN Excludes Non-Matches

The join condition `ON o.customer_id = c.customer_id` is evaluated for every combination of rows (conceptually). Only pairs where the condition is TRUE make it into the result. This is different from:

- **LEFT JOIN**: keeps all rows from the left (orders) table, even with no match
- **FULL OUTER JOIN**: keeps all rows from both tables, NULL-filling the side with no match

## The Danger of NULL in Join Columns

Since `NULL = NULL` evaluates to UNKNOWN (not TRUE), if `customer_id` is NULL in the orders table, that order will **never** match any customer — even if the customers table also has a NULL id. This is correct SQL behavior but surprises many beginners.

## Real-World Join Design

In a well-designed schema, the join column (`customer_id` in `orders`) is a **foreign key** referencing the primary key of the parent table (`id` in `customers`). SQL Server enforces referential integrity if you declare the constraint:

```sql
ALTER TABLE dbo.orders
ADD CONSTRAINT fk_orders_customer
    FOREIGN KEY (customer_id) REFERENCES dbo.customers(id);
```

With this constraint active, an `INSERT` into `orders` with a non-existent `customer_id` will fail with an error rather than creating an orphaned record.

## Multi-Table Joins

In practice you chain many joins:

```sql
SELECT o.id, c.name, p.sku, od.qty
FROM   dbo.orders       AS o
JOIN   dbo.customers    AS c  ON c.id = o.customer_id
JOIN   dbo.order_items  AS od ON od.order_id = o.id
JOIN   dbo.products     AS p  ON p.id = od.product_id;
```

Each join introduces a new table into the query. The optimizer decides the best join order.

## In This Exercise

You will receive two tables as input and perform the INNER JOIN logic in Python. The result should be sorted by `order_id` ascending — mirroring `ORDER BY o.order_id` in SQL.

> **Further reading:** *SQL Notes for Professionals* (GoalKicker) — Chapters on JOINs with worked examples, free at https://books.goalkicker.com/SQLBook/

> **MIT OCW 1.264J** has hands-on SQL Server lab exercises covering multi-table joins — free at https://ocw.mit.edu/courses/1-264j-database-internet-and-systems-integration-technologies-fall-2013/pages/lecture-notes-exercises/
