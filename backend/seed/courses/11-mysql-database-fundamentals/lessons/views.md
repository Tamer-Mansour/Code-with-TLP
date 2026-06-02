# Views

A **view** is a named, saved SELECT query. Once created, you can query it like a regular table. Views don't store data — they execute the underlying query on demand — but they provide a powerful layer of abstraction over complex or sensitive data.

## Creating a view

```sql
CREATE VIEW active_user_orders AS
SELECT
    u.id         AS user_id,
    u.email,
    COUNT(o.id)  AS order_count,
    SUM(o.total) AS lifetime_value
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.is_active = 1
GROUP BY u.id, u.email;
```

Query it like a table:

```sql
SELECT * FROM active_user_orders WHERE lifetime_value > 500;
```

## Benefits of views

- **Simplification** — hide complex joins and aggregations behind a simple name.
- **Security** — grant users SELECT on the view without exposing base tables or sensitive columns (e.g., hide `password_hash`).
- **Consistency** — one definition of "active user" used by every query and every developer.

## Updatable vs read-only views

MySQL allows `INSERT`/`UPDATE`/`DELETE` through a view if it meets strict conditions:

- Maps to exactly one base table.
- Does not use `DISTINCT`, aggregate functions, `GROUP BY`, `HAVING`, `UNION`, or subqueries in `FROM`.
- Does not use derived columns for modification.

The view above uses `GROUP BY` and aggregates, so it is **read-only**. Attempting to `INSERT` into it will fail with an error.

## WITH CHECK OPTION

When a view is updatable you can add `WITH CHECK OPTION` to ensure rows inserted or updated through the view still satisfy the view's `WHERE` clause:

```sql
CREATE VIEW active_users AS
SELECT * FROM users WHERE is_active = 1
WITH CHECK OPTION;

-- This INSERT will be rejected because is_active = 0 doesn't pass the view filter:
INSERT INTO active_users (email, is_active) VALUES ('new@example.com', 0);
```

## Modifying and dropping views

```sql
-- Replace an existing view definition
CREATE OR REPLACE VIEW active_user_orders AS
SELECT ...;   -- new definition

-- Drop a view
DROP VIEW IF EXISTS active_user_orders;
```

## SHOW CREATE VIEW

```sql
SHOW CREATE VIEW active_user_orders\G
```

This shows the exact stored definition, including the security context (definer vs invoker).

## Security: DEFINER vs INVOKER

By default, views run with the privileges of the view's creator (`DEFINER`). That means a low-privilege user can query the view and get results even if they can't directly SELECT from the base tables. Change this with `SQL SECURITY INVOKER` if you want the view to run with the calling user's own privileges.

```sql
CREATE DEFINER = 'app_user'@'%'
  SQL SECURITY DEFINER
  VIEW public_products AS
  SELECT id, name, price FROM products WHERE is_published = 1;
```

## Views vs materialized views

MySQL does not have native materialized views (unlike PostgreSQL). A workaround is a summary table populated by an event or a scheduled job:

```sql
CREATE TABLE mv_user_stats AS SELECT ... FROM users JOIN orders ...;
-- Refresh with a scheduled event or cron job
TRUNCATE mv_user_stats;
INSERT INTO mv_user_stats SELECT ...;
```

For true read-heavy analytics, consider exporting to a data warehouse (BigQuery, Redshift) rather than fighting MySQL's query planner.
