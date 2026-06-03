# Challenge: 20 SQL Queries

Writing SQL by hand is the fastest way to internalise how MySQL thinks. In this challenge you'll write 20 queries of increasing difficulty against a small e-commerce schema — moving from simple `SELECT` filters all the way to multi-table joins, grouping, and subqueries. The goal is fluency: being able to translate a plain-English question into correct, efficient SQL without reaching for an ORM.

## The schema

All queries run against three tables. Create them in MySQL 8 before you start:

```sql
CREATE TABLE customers (
    id        INT PRIMARY KEY AUTO_INCREMENT,
    name      VARCHAR(100) NOT NULL,
    city      VARCHAR(50),
    joined_at DATE NOT NULL
);

CREATE TABLE products (
    id    INT PRIMARY KEY AUTO_INCREMENT,
    name  VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE orders (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    product_id  INT NOT NULL,
    quantity    INT NOT NULL,
    ordered_at  DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id)  REFERENCES products(id)
);
```

## The 20 questions

Work through them in order — each builds on the last.

| #  | Question | Key concept |
|----|----------|-------------|
| 1  | All customers, sorted by name | `ORDER BY` |
| 2  | Products priced above 100 | `WHERE` + comparison |
| 3  | Customers from 'Cairo' | equality filter |
| 4  | The 5 cheapest products | `ORDER BY ... LIMIT` |
| 5  | Distinct cities customers live in | `DISTINCT` |
| 6  | Products whose name contains 'pro' | `LIKE '%pro%'` |
| 7  | Count of customers | `COUNT(*)` |
| 8  | Average product price | `AVG()` |
| 9  | Total revenue per product | `SUM(price*quantity)`, `GROUP BY` |
| 10 | Number of orders per customer | `GROUP BY` |
| 11 | Customers with more than 3 orders | `GROUP BY` + `HAVING` |
| 12 | Each order with the customer's name | `INNER JOIN` |
| 13 | All customers, even those with no orders | `LEFT JOIN` |
| 14 | Customers who never ordered | `LEFT JOIN ... IS NULL` |
| 15 | Most expensive product | subquery / `MAX()` |
| 16 | Products never ordered | `NOT IN (subquery)` |
| 17 | Orders placed in 2025 | date range filter |
| 18 | Top 3 customers by total spend | join + `GROUP BY` + `LIMIT` |
| 19 | Customers who spent above the average | subquery in `HAVING` |
| 20 | Running list of products with their order count, including zero | `LEFT JOIN` + `COUNT` |

## Worked examples

**Query 9 — total revenue per product:**

```sql
SELECT p.name,
       SUM(p.price * o.quantity) AS revenue
FROM products p
JOIN orders o ON o.product_id = p.id
GROUP BY p.id, p.name
ORDER BY revenue DESC;
```

**Query 18 — top 3 customers by total spend:**

```sql
SELECT c.name,
       SUM(p.price * o.quantity) AS total_spent
FROM customers c
JOIN orders o   ON o.customer_id = c.id
JOIN products p ON p.id = o.product_id
GROUP BY c.id, c.name
ORDER BY total_spent DESC
LIMIT 3;
```

## Common mistakes

- **Selecting non-grouped columns.** In MySQL 8 with `ONLY_FULL_GROUP_BY` enabled (the default), every column in `SELECT` must either appear in `GROUP BY` or be inside an aggregate. Add the column to `GROUP BY` rather than disabling the mode.
- **`WHERE` vs `HAVING`.** `WHERE` filters rows *before* grouping; `HAVING` filters *after*, so aggregate conditions like `COUNT(*) > 3` belong in `HAVING`.
- **Using `=` with `NULL`.** `city = NULL` is never true. Use `IS NULL` / `IS NOT NULL`.
- **Forgetting the join condition.** A join without `ON` produces a cartesian product — every row paired with every other.

## Best practices

- Always qualify columns with table aliases (`c.name`, `o.quantity`) in multi-table queries to avoid ambiguity.
- Prefer `JOIN` over `IN (subquery)` when you need columns from both tables — it's usually clearer and faster.
- Run `EXPLAIN <query>;` to confirm indexes are being used on large tables.

**Summary:** These 20 queries cover the core SQL you'll use daily as a Spring backend developer — filtering, aggregating, joining, and subquerying. Master them by hand and the JPA/Hibernate layer you build later will make far more sense.
