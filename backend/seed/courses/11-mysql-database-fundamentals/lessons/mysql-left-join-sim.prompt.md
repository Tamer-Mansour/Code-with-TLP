# LEFT JOIN Simulation

## Problem

Simulate MySQL's `LEFT JOIN` behavior between two tables (A and B), joined on their `id` column.

This replicates:
```sql
SELECT a.id, a.value_a, b.value_b
FROM table_a a
LEFT JOIN table_b b ON b.id = a.id
ORDER BY a.id;
```

**Input format:**

```
N
id1 value_a1
id2 value_a2
...   (N rows of table A)
M
id1 value_b1
id2 value_b2
...   (M rows of table B)
```

- First line: `N`, number of rows in table A
- Next N lines: rows of table A as `id value_a`
- Next line: `M`, number of rows in table B
- Next M lines: rows of table B as `id value_b`
- IDs are positive integers; values are single-word strings

**Output:**

One line per row in table A (left table), in format `id value_a value_b`, sorted by `id` **ascending**. Use the literal word `NULL` for missing `value_b` (when no matching row exists in B).

## Example

**Input:**
```
4
1 Apple
2 Banana
3 Cherry
5 Date
3
1 Red
3 Green
4 Blue
```

**Output:**
```
1 Apple Red
2 Banana NULL
3 Cherry Green
5 Date NULL
```

**Explanation:**
- id=1: matches B → Red
- id=2: no match in B → NULL
- id=3: matches B → Green
- id=4: exists in B but NOT in A → excluded (left join keeps only A rows)
- id=5: no match in B → NULL

## Constraints

- `1 <= N, M <= 500`
- All IDs are positive integers
- Each ID appears at most once in each table
- Values are single-word alphanumeric strings
