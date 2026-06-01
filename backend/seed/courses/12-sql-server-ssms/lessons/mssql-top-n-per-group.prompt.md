# Top-N Per Group

Simulate this T-SQL query in Python:

```sql
WITH ranked AS (
  SELECT category, score,
         ROW_NUMBER() OVER (PARTITION BY category ORDER BY score DESC) AS rn
  FROM entries
)
SELECT category, score FROM ranked WHERE rn <= :K;
```

## Input

```
N K
<row 1: category,score>
<row 2: category,score>
...
<row N: category,score>
```

- `N` is the number of rows (1 ≤ N ≤ 10000).
- `K` is the top-N to keep per group (1 ≤ K ≤ N).
- Each row is `category,score` where `category` is a non-empty string without commas and `score` is an integer.

## Output

For each category, in **first-seen** input order, print the top-K rows sorted by **score descending**. If a category has fewer than K rows, print all of them.

Format each output line as `category,score`.

## Example

Input:

```
5 2
A,10
A,20
A,30
B,5
B,15
```

Output:

```
A,30
A,20
B,15
B,5
```

(Groups appear in the order they first appeared: A then B. Within each, scores descend.)
