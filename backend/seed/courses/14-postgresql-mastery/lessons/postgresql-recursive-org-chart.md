# Exercise: Recursive Org Chart Depth

In this exercise you will simulate PostgreSQL's `WITH RECURSIVE` CTE by computing the depth of each node in an employee hierarchy.

## Background

PostgreSQL's recursive CTEs use a fixed-point iteration model: the anchor query produces the starting rows, then the recursive term is evaluated repeatedly — joining against the accumulated result — until no new rows appear. This is how queries like org chart traversal, bill-of-materials explosion, and category tree walks work in SQL.

```sql
WITH RECURSIVE org AS (
  -- Anchor: find the root (CEO)
  SELECT id, manager_id, 0 AS depth
  FROM employees
  WHERE manager_id IS NULL

  UNION ALL

  -- Recursive: find direct reports of everyone found so far
  SELECT e.id, e.manager_id, org.depth + 1
  FROM employees e
  JOIN org ON e.manager_id = org.id
)
SELECT * FROM org ORDER BY id;
```

The key insight: depth is 0 for roots, and each child's depth is parent's depth + 1. The BFS traversal naturally mirrors what Postgres does internally.

## Your Task

Implement this recursive traversal in Python, reading employee-manager pairs from stdin and printing each employee's depth to stdout. See the prompt for full input/output specification.

## Reference

- [PostgreSQL Official Documentation — CTEs](https://www.postgresql.org/docs/current/queries-with.html) — covers `WITH RECURSIVE`, cycle detection (Postgres 14+), and search order options.
- [PostgreSQL Notes for Professionals](https://books.goalkicker.com/PostgreSQLBook/) — Chapter on recursive queries with practical org-chart examples.
