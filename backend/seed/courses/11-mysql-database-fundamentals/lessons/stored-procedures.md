# Stored Procedures

A **stored procedure** is a named, pre-compiled block of SQL stored inside the database server. Instead of sending a multi-statement query from your application every time, you call the procedure by name and the server executes it. This reduces round-trips, centralizes business logic, and can be secured independently from the underlying tables.

## Creating a simple procedure

```sql
DELIMITER $$

CREATE PROCEDURE greet_user(IN username VARCHAR(100))
BEGIN
    SELECT CONCAT('Hello, ', username, '!') AS greeting;
END$$

DELIMITER ;
```

Call it:

```sql
CALL greet_user('Tamer');
-- Returns: Hello, Tamer!
```

`DELIMITER $$` tells the MySQL client to use `$$` as the statement terminator so the semicolons inside the procedure body don't end the `CREATE` statement prematurely.

## IN, OUT, and INOUT parameters

| Mode | Direction | Use case |
|---|---|---|
| `IN` | Caller → procedure | Pass a filter value |
| `OUT` | Procedure → caller | Return a single computed value |
| `INOUT` | Both | Read then modify a variable |

```sql
DELIMITER $$

CREATE PROCEDURE get_order_total(
    IN  p_order_id INT,
    OUT p_total    DECIMAL(10,2)
)
BEGIN
    SELECT SUM(quantity * unit_price)
      INTO p_total
      FROM order_items
     WHERE order_id = p_order_id;
END$$

DELIMITER ;

-- Usage
CALL get_order_total(42, @total);
SELECT @total;
```

## Variables and control flow

Procedures support local variables, `IF/ELSEIF/ELSE`, and `WHILE`/`REPEAT` loops:

```sql
DELIMITER $$

CREATE PROCEDURE categorize_order(IN p_amount DECIMAL(10,2), OUT p_tier VARCHAR(20))
BEGIN
    IF p_amount >= 1000 THEN
        SET p_tier = 'platinum';
    ELSEIF p_amount >= 250 THEN
        SET p_tier = 'gold';
    ELSE
        SET p_tier = 'standard';
    END IF;
END$$

DELIMITER ;
```

## Error handling with DECLARE ... HANDLER

```sql
DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
BEGIN
    ROLLBACK;
    SET p_result = 'ERROR';
END;
```

Place handler declarations after variable declarations but before any SQL statements.

## Listing and dropping procedures

```sql
-- Show all procedures in the current database
SHOW PROCEDURE STATUS WHERE Db = DATABASE();

-- See the definition
SHOW CREATE PROCEDURE get_order_total\G

-- Remove a procedure
DROP PROCEDURE IF EXISTS get_order_total;
```

## When to use stored procedures

Stored procedures shine when:

- You need the same multi-step logic called from several different application stacks.
- You want to grant execute permission without exposing the underlying tables.
- You're migrating a legacy system where the database already contains business logic.

They are less ideal when you want version-controlled, easily testable logic — application code in a language like Go or Python with migrations is usually more maintainable for greenfield projects.
