# INNER and OUTER Joins

A **join** combines rows from two tables based on a matching column. It's how you traverse the relationships your foreign keys describe.

## Setup

```sql
CREATE TABLE users  (id INT PRIMARY KEY, name VARCHAR(50));
CREATE TABLE orders (id INT PRIMARY KEY, user_id INT, amount INT);

INSERT INTO users  VALUES (1,'Alice'), (2,'Bob'), (3,'Carol');
INSERT INTO orders VALUES (10, 1, 100), (11, 1, 50), (12, 2, 30);
```

`Carol` has no orders; `Alice` has two.

## INNER JOIN

Returns only rows where the join condition is true on **both** sides.

```sql
SELECT u.name, o.amount
FROM users u
INNER JOIN orders o ON o.user_id = u.id;
```

```
name  | amount
------+-------
Alice | 100
Alice |  50
Bob   |  30
```

Carol is missing — no matching order.

## LEFT JOIN

Returns every row from the **left** table, plus matched rows from the right (or `NULL` if no match).

```sql
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;
```

```
name  | amount
------+-------
Alice | 100
Alice |  50
Bob   |  30
Carol | NULL
```

## RIGHT JOIN

The mirror of `LEFT JOIN`. Rarely needed — just flip the table order and use `LEFT JOIN`.

## Finding rows that DON'T match

A famous LEFT JOIN trick: rows in the left table with **no** match in the right.

```sql
SELECT u.*
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id IS NULL;          -- "no order existed"
```

## CROSS JOIN

Cartesian product — every row on the left paired with every row on the right.

```sql
SELECT u.name, t.tag
FROM users u
CROSS JOIN tags t;
```

If `users` has 1000 rows and `tags` has 50, you get 50,000 rows. Useful for generating combinations; dangerous by accident.

## Multi-table joins

Joins chain. Read them from left to right:

```sql
SELECT u.name, p.title, c.body
FROM users u
JOIN posts p     ON p.user_id = u.id
JOIN comments c  ON c.post_id = p.id
WHERE u.id = 42;
```

## Join performance

Joins are fast when the **join column on the right side is indexed** (and ideally on the left too). Without an index, every left row triggers a full scan of the right table — `O(n²)`.

The most common production performance issue with joins isn't the join itself — it's a missing index on the foreign-key column.

## Aliases

`AS` is optional and almost always omitted for table aliases:

```sql
SELECT u.name FROM users u JOIN orders o ON o.user_id = u.id;
```

Short aliases make complex joins readable. Use them.
