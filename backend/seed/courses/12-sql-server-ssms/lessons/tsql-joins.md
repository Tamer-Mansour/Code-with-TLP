# Joins in T-SQL

Joining tables is the backbone of relational queries. T-SQL supports all standard join types plus a few Microsoft-flavored details worth knowing.

## INNER JOIN

Returns only rows with a match in both tables.

```sql
SELECT o.id, o.amount, c.name
FROM   dbo.orders   AS o
INNER JOIN dbo.customers AS c ON o.customer_id = c.id
WHERE  o.status = 'paid';
```

`INNER` is the default — `JOIN` alone means `INNER JOIN`. Be explicit for readability.

## LEFT (OUTER) JOIN

Returns all rows from the left table; NULL-fills the right side when there is no match.

```sql
SELECT c.name, o.id AS order_id
FROM   dbo.customers AS c
LEFT JOIN dbo.orders AS o ON o.customer_id = c.id;
```

Customers with no orders appear once with `order_id = NULL`. This is the go-to for "show everything, even if nothing matches."

## RIGHT JOIN and FULL OUTER JOIN

`RIGHT JOIN` mirrors `LEFT JOIN` — all right-table rows kept. In practice, most developers flip the table order and use a `LEFT JOIN` instead; it reads more naturally.

`FULL OUTER JOIN` keeps all rows from both sides, NULL-filling whichever side has no match. Useful for comparing two lists to find items present in only one:

```sql
SELECT a.id AS a_id, b.id AS b_id
FROM   dbo.table_a AS a
FULL OUTER JOIN dbo.table_b AS b ON a.id = b.id
WHERE  a.id IS NULL OR b.id IS NULL;   -- symmetric difference
```

## CROSS JOIN

Every row of the left table combined with every row of the right — a Cartesian product. Use with deliberate care, typically to generate combinations or test data.

```sql
SELECT color, size FROM dbo.colors CROSS JOIN dbo.sizes;
```

## Self Join

A table joined to itself. Classic use: hierarchical data (employees and their managers).

```sql
SELECT e.name AS employee, m.name AS manager
FROM   dbo.employees AS e
LEFT JOIN dbo.employees AS m ON e.manager_id = m.id;
```

## Multi-Table Join Chaining

You can chain as many joins as you need. SQL Server processes them left-to-right unless the optimizer reorders them. Keep the join columns indexed.

```sql
SELECT o.id, c.name, p.sku, od.qty
FROM   dbo.orders       AS o
JOIN   dbo.customers    AS c  ON c.id = o.customer_id
JOIN   dbo.order_items  AS od ON od.order_id = o.id
JOIN   dbo.products     AS p  ON p.id = od.product_id
WHERE  o.created_at >= '2025-01-01';
```

## Tips

| Tip | Why |
|-----|-----|
| Always alias tables | Avoids ambiguous column references |
| Join on indexed columns | Dramatically reduces scans |
| Filter early with WHERE | The optimizer can push predicates into the join |
| Avoid implicit joins (comma syntax) | `FROM a, b WHERE a.id = b.x` is T-SQL legal but hard to read — always use explicit `JOIN` |

## APPLY Operators (T-SQL Extension)

`CROSS APPLY` and `OUTER APPLY` are T-SQL extensions that invoke a table-valued expression for each row of the outer query — think of them as a row-by-row lateral join.

```sql
-- Return the latest 3 orders per customer
SELECT c.id, c.name, recent.id AS order_id, recent.amount
FROM   dbo.customers AS c
CROSS APPLY (
    SELECT TOP 3 id, amount
    FROM dbo.orders
    WHERE customer_id = c.id
    ORDER BY created_at DESC
) AS recent;
```

`OUTER APPLY` behaves like a `LEFT JOIN` — it keeps customers even when the inner query returns no rows.
