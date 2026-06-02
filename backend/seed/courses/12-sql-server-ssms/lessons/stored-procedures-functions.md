# Stored Procedures and User-Defined Functions

Server-side code that encapsulates logic, improves performance through plan reuse, and centralizes business rules — three of the most important tools in a SQL Server developer's kit.

## Stored Procedures

A stored procedure is a named, compiled batch of T-SQL that lives in the database and can be called by name.

```sql
CREATE OR ALTER PROCEDURE dbo.GetCustomerOrders
    @customer_id INT,
    @since       DATE = NULL        -- optional parameter with default
AS
BEGIN
    SET NOCOUNT ON;                 -- suppress "rows affected" messages

    IF @since IS NULL
        SET @since = DATEADD(year, -1, GETDATE());

    SELECT o.id, o.amount, o.status, o.created_at
    FROM   dbo.orders AS o
    WHERE  o.customer_id = @customer_id
      AND  o.created_at >= @since
    ORDER BY o.created_at DESC;
END;
GO
```

Execute it:

```sql
EXEC dbo.GetCustomerOrders @customer_id = 42;
EXEC dbo.GetCustomerOrders @customer_id = 42, @since = '2025-01-01';
```

### Why use stored procedures?

- **Plan caching** — SQL Server compiles and caches the execution plan on first call. Subsequent calls reuse it.
- **Security** — grant `EXECUTE` on the procedure without granting direct table access.
- **Atomicity** — wrap a multi-step operation in a single server-side call.

### Output parameters

```sql
CREATE OR ALTER PROCEDURE dbo.CountOrders
    @customer_id INT,
    @total       INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @total = COUNT(*) FROM dbo.orders WHERE customer_id = @customer_id;
END;
GO

DECLARE @n INT;
EXEC dbo.CountOrders @customer_id = 42, @total = @n OUTPUT;
SELECT @n AS total_orders;
```

## Scalar User-Defined Functions

Returns a single value. Use sparingly — scalar UDFs applied to table columns can prevent parallelism and cause row-by-row execution.

```sql
CREATE OR ALTER FUNCTION dbo.FormatPhone (@phone NVARCHAR(20))
RETURNS NVARCHAR(20)
AS
BEGIN
    RETURN '(' + SUBSTRING(@phone,1,3) + ') ' +
           SUBSTRING(@phone,4,3) + '-' +
           SUBSTRING(@phone,7,4);
END;
GO

SELECT dbo.FormatPhone(phone) FROM dbo.customers;
```

## Inline Table-Valued Functions (iTVF)

Returns a table and is inlined by the optimizer — essentially a parameterized view. Prefer iTVFs over scalar UDFs for performance.

```sql
CREATE OR ALTER FUNCTION dbo.GetTopOrders
    (@customer_id INT, @top_n INT)
RETURNS TABLE
AS
RETURN
    SELECT TOP (@top_n) id, amount, created_at
    FROM   dbo.orders
    WHERE  customer_id = @customer_id
    ORDER BY amount DESC;
GO

-- Use like a table:
SELECT * FROM dbo.GetTopOrders(42, 5);
```

## Quick Comparison

| Feature | Stored Proc | Scalar UDF | Inline TVF |
|---------|------------|-----------|-----------|
| Returns | Result sets + output params | Single value | Table |
| Can modify data | Yes | No | No |
| Optimizer inlining | N/A | Limited (SQL 2019+) | Yes |
| Use in SELECT list | No | Yes | Yes (JOIN/CROSS APPLY) |

## Dropping and Altering

```sql
DROP PROCEDURE IF EXISTS dbo.GetCustomerOrders;
DROP FUNCTION  IF EXISTS dbo.GetTopOrders;
```

`CREATE OR ALTER` (SQL Server 2016+) is the safest pattern — it creates if absent, replaces if present, preserves permissions.
