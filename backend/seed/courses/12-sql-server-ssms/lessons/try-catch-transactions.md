# Error Handling with TRY...CATCH and Transactions

Reliable SQL Server code handles failures gracefully and leaves the database consistent. TRY...CATCH combined with explicit transactions is the standard pattern.

## TRY...CATCH

Structure mirrors try/catch in application languages:

```sql
BEGIN TRY
    -- Code that might fail
    INSERT INTO dbo.orders (customer_id, amount) VALUES (999, 100.00);
    UPDATE dbo.inventory SET qty = qty - 1 WHERE product_id = 7;
END TRY
BEGIN CATCH
    -- Runs only when an error is raised inside the TRY block
    SELECT
        ERROR_NUMBER()    AS error_number,
        ERROR_SEVERITY()  AS severity,
        ERROR_STATE()     AS state,
        ERROR_PROCEDURE() AS proc_name,
        ERROR_LINE()      AS line_number,
        ERROR_MESSAGE()   AS message;
END CATCH;
```

Key error functions available inside `CATCH`:

| Function | Returns |
|----------|---------|
| `ERROR_NUMBER()` | The SQL Server error code |
| `ERROR_MESSAGE()` | The human-readable description |
| `ERROR_SEVERITY()` | 0–25 severity level |
| `ERROR_STATE()` | Disambiguates errors with the same number |
| `ERROR_LINE()` | Line number inside the batch/procedure |

## Combining with Transactions

Without an explicit transaction, each statement auto-commits. Wrap related statements so they all succeed or all roll back.

```sql
BEGIN TRY
    BEGIN TRANSACTION;

    UPDATE dbo.accounts SET balance = balance - 500 WHERE id = 1;
    UPDATE dbo.accounts SET balance = balance + 500 WHERE id = 2;

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    -- Log the error or re-raise it
    THROW;   -- re-raises the caught error to the caller (SQL 2012+)
END CATCH;
```

`@@TRANCOUNT` holds the nesting depth of open transactions. Always check it before rolling back to avoid rolling back a transaction you didn't open.

## THROW vs RAISERROR

`THROW` (SQL Server 2012+) is the modern way to raise or re-raise errors:

```sql
THROW 50001, 'Amount cannot be negative', 1;
```

`RAISERROR` is the legacy alternative, still widely used:

```sql
RAISERROR('Amount cannot be negative', 16, 1);
```

Prefer `THROW` in new code — it preserves the original error number when re-raising and has cleaner syntax.

## Savepoints

Nested transactions let you roll back part of a unit of work:

```sql
BEGIN TRANSACTION;

    INSERT INTO dbo.audit_log (msg) VALUES ('Started');

    SAVE TRANSACTION before_risky_part;

    BEGIN TRY
        DELETE FROM dbo.orders WHERE amount < 0;   -- might fail
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION before_risky_part;    -- roll back to savepoint only
    END CATCH;

COMMIT TRANSACTION;
```

## Pattern: Error Logging Procedure

A common production pattern is a dedicated error-logging procedure called from every CATCH block:

```sql
CREATE OR ALTER PROCEDURE dbo.LogError
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.error_log (error_number, message, captured_at)
    VALUES (ERROR_NUMBER(), ERROR_MESSAGE(), SYSUTCDATETIME());
END;
GO
```

Then in every CATCH:

```sql
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    EXEC dbo.LogError;
    THROW;
END CATCH;
```

This keeps error handling consistent across the entire application database layer.
