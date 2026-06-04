# Exercise: Simulate a SELECT with WHERE Filter

SQL's `WHERE` clause is the engine of data retrieval — it lets you express a predicate that each candidate row must satisfy before it appears in your result set.

## The SQL Behind This Exercise

In T-SQL you would write something like:

```sql
SELECT id, name, department, salary
FROM   dbo.employees
WHERE  department = 'Engineering'
  AND  salary >= 60000
ORDER BY id;  -- preserve original id order
```

The engine evaluates the `WHERE` predicate row by row (conceptually). Only rows where **both** conditions are `TRUE` pass through. When you have multiple conditions joined by `AND`, all of them must hold.

## Comparison Operators in T-SQL

| Operator | Meaning |
|----------|---------|
| `=`      | Equal |
| `<>` or `!=` | Not equal |
| `>`      | Greater than |
| `>=`     | Greater than or equal |
| `<`      | Less than |
| `<=`     | Less than or equal |
| `BETWEEN x AND y` | Inclusive range (same as `>= x AND <= y`) |
| `IN (a, b, c)` | Matches any value in the list |
| `LIKE 'pat%'` | Pattern match with wildcards |

## Logical Operators

`AND`, `OR`, and `NOT` combine predicates. Operator precedence: `NOT` > `AND` > `OR`. Use parentheses when you have mixed operators — do not rely on precedence for readability.

```sql
-- Without explicit parentheses this can surprise you:
WHERE dept = 'Eng' OR dept = 'HR' AND salary > 70000
-- SQL Server evaluates AND first, so it means:
WHERE dept = 'Eng' OR (dept = 'HR' AND salary > 70000)
```

## Strings Use Single Quotes

T-SQL string literals require **single quotes**. Double quotes delimit identifiers:

```sql
WHERE department = 'Engineering'   -- correct: string literal
WHERE department = "Engineering"   -- WRONG: "Engineering" is a column name
```

This is one of the most common bugs for developers coming from MySQL.

## In This Exercise

You will receive employee records and apply the same two-condition filter in Python. The goal is to internalize the **logic** of a WHERE clause — each row is tested independently, and original order is preserved.

> **Further reading:** *SQL Notes for Professionals* (GoalKicker) — Chapter on SELECT and WHERE filters, available free at https://books.goalkicker.com/SQLBook/
