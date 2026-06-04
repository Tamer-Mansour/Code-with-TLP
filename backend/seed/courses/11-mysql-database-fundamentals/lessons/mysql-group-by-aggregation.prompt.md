# GROUP BY Aggregation

## Problem

Simulate a SQL `GROUP BY` query. You are given N sales records. For each unique product, compute the total number of sales and the average sale amount.

This replicates the query:
```sql
SELECT product, COUNT(*), ROUND(AVG(amount), 2)
FROM sales
GROUP BY product
ORDER BY product;
```

**Input format:**

```
N
product1 amount1
product2 amount2
...
```

- First line: `N`, the number of sales records
- Each following line: a product name (no spaces) and a sale amount (a decimal number)

**Output:**

One line per unique product, sorted by product name **ascending (alphabetical)**:

```
product count avg_amount
```

Where `avg_amount` is rounded to **exactly 2 decimal places** (e.g., `3.33`, `2.50`, `5.00`).

## Example

**Input:**
```
6
Apple 3.50
Banana 2.00
Apple 4.50
Banana 3.00
Apple 2.00
Cherry 5.00
```

**Output:**
```
Apple 3 3.33
Banana 2 2.50
Cherry 1 5.00
```

## Constraints

- `1 <= N <= 1000`
- Product names are alphabetic strings with no spaces
- Amounts are positive decimals with up to 2 decimal places
- There will be at least 1 unique product
