# Top-N Per Group

The classic window-function task: for each `category`, return the top-K rows by score.

T-SQL:

```sql
WITH ranked AS (
  SELECT category, score,
         ROW_NUMBER() OVER (PARTITION BY category ORDER BY score DESC) AS rn
  FROM dbo.entries
)
SELECT category, score
FROM ranked
WHERE rn <= @k;
```

In this exercise you'll simulate that in Python. Each group's rows must come out in **score-descending** order, and the groups themselves must appear in **first-seen order** from the input.

See the prompt file for I/O details.
