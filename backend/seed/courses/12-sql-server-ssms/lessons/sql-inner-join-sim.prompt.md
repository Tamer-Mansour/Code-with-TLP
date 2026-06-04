# Simulate an INNER JOIN

## Problem

You are given two tables as input.

**Table 1 — Orders** has `M` rows, each containing `order_id` and `customer_id`.

**Table 2 — Customers** has `K` rows, each containing `customer_id` and `customer_name`.

Perform an **INNER JOIN** on `customer_id` and print each matching row as `order_id,customer_name`, **sorted by `order_id` ascending**.

Orders with no matching customer are excluded — just like a SQL `INNER JOIN`.

This simulates:
```sql
SELECT o.order_id, c.customer_name
FROM   orders    AS o
INNER JOIN customers AS c ON o.customer_id = c.customer_id
ORDER BY o.order_id;
```

## Input Format

- Line 1: integer `M` — number of order rows
- Next `M` lines: `order_id,customer_id` (both positive integers)
- Next line: integer `K` — number of customer rows
- Next `K` lines: `customer_id,customer_name`

## Output Format

One line per matched row: `order_id,customer_name`, sorted by `order_id` ascending. If no rows match, print nothing.

## Constraints

- `1 <= M <= 1000`
- `1 <= K <= 1000`
- `order_id` values are unique
- `customer_id` values in the customers table are unique
- Customer names contain no commas

## Example

**Input:**
```
4
101,1
102,3
103,2
104,5
3
1,Alice
2,Bob
3,Carol
```

**Output:**
```
101,Alice
102,Carol
103,Bob
```

Order 104 has `customer_id = 5`, which does not exist in the customers table, so it is excluded.
