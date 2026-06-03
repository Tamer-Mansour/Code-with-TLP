# Exception Handling

Every real program encounters conditions it did not expect: a file that does not exist, a network timeout, a user who types letters where a number was required. Java's exception system gives you a structured, type-safe way to detect those conditions, react to them, and release resources cleanly — without scattering error codes through every method signature.

## The Exception Hierarchy

All throwable objects extend `java.lang.Throwable`. The two main branches are:

| Branch | Root class | Must be caught/declared? | Typical cause |
|---|---|---|---|
| Checked exceptions | `Exception` (excluding `RuntimeException`) | Yes | External failure (I/O, SQL, network) |
| Unchecked exceptions | `RuntimeException` | No | Programming errors (null, bad index) |
| Errors | `Error` | No (almost never) | JVM-level problem (`OutOfMemoryError`) |

Common examples you will see throughout this course:

- `IOException`, `FileNotFoundException` — file and stream operations
- `SQLException` — JDBC / MySQL queries
- `NullPointerException`, `IllegalArgumentException` — unchecked logic errors
- `NumberFormatException` — parsing a string like `"abc"` as an integer

## try / catch / finally

```java
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class FileReader {

    public static void main(String[] args) {
        try {
            String content = Files.readString(Path.of("data.txt"));
            System.out.println(content);
        } catch (IOException e) {
            System.err.println("Could not read file: " + e.getMessage());
        } finally {
            // Runs whether or not an exception occurred
            System.out.println("Done.");
        }
    }
}
```

Key rules:
- A `try` block can have multiple `catch` clauses — list them from most specific to most general.
- The `finally` block always executes (even after a `return` inside `try`). Use it to release resources.
- You can catch multiple unrelated exceptions in one clause with `|`: `catch (IOException | SQLException e)`.

## try-with-resources (Preferred for I/O)

Any object that implements `AutoCloseable` can be declared in the `try(...)` header. The JVM calls `close()` automatically — even if an exception is thrown — which is safer than relying on a `finally` block.

```java
import java.sql.*;

public class DatabaseExample {

    private static final String URL = "jdbc:mysql://localhost:3306/mydb";

    public static void printUsers(Connection conn) throws SQLException {
        String sql = "SELECT id, username FROM users";

        try (PreparedStatement stmt = conn.prepareStatement(sql);
             ResultSet rs = stmt.executeQuery()) {

            while (rs.next()) {
                System.out.printf("%d  %s%n", rs.getInt("id"), rs.getString("username"));
            }
        }
        // stmt and rs are closed here automatically
    }
}
```

This pattern is the standard throughout Spring Boot's JDBC layer and is the first thing code-reviewers check.

## Throwing Exceptions

Use `throw` to raise an exception, and `throws` on the method signature to declare checked exceptions the caller must handle.

```java
public class BankAccount {

    private double balance;

    public BankAccount(double initialBalance) {
        if (initialBalance < 0) {
            throw new IllegalArgumentException(
                "Initial balance cannot be negative: " + initialBalance);
        }
        this.balance = initialBalance;
    }

    public void withdraw(double amount) throws Exception {
        if (amount > balance) {
            throw new Exception("Insufficient funds. Balance: " + balance);
        }
        balance -= amount;
    }
}
```

## Creating Custom Exceptions

Define a custom exception whenever you want callers to distinguish your domain error from generic ones.

```java
// Checked custom exception
public class InsufficientFundsException extends Exception {

    private final double shortfall;

    public InsufficientFundsException(double shortfall) {
        super(String.format("Insufficient funds — %.2f more required.", shortfall));
        this.shortfall = shortfall;
    }

    public double getShortfall() {
        return shortfall;
    }
}
```

Usage:

```java
public void withdraw(double amount) throws InsufficientFundsException {
    if (amount > balance) {
        throw new InsufficientFundsException(amount - balance);
    }
    balance -= amount;
}
```

Callers can now `catch (InsufficientFundsException e)` and read `e.getShortfall()` for richer error handling — something impossible with a plain `Exception`.

## Common Mistakes and Best Practices

- **Never swallow exceptions silently.** An empty `catch` block hides bugs permanently.
  ```java
  // Bad
  catch (IOException e) { }

  // Good
  catch (IOException e) { log.error("Failed to read config", e); }
  ```

- **Do not use exceptions for normal control flow.** Throwing an exception to signal "list is empty" is expensive and misleading.

- **Preserve the cause when re-throwing.** Pass the original exception as the `cause` argument so stack traces chain correctly.
  ```java
  catch (SQLException e) {
      throw new RuntimeException("Database lookup failed", e); // cause preserved
  }
  ```

- **Prefer specific catch types over `Exception`.** Catching `Exception` can accidentally hide `NullPointerException` or other bugs you did not intend to handle.

- **Use `throws` declarations honestly.** If a method truly cannot recover from a checked exception, declare it and let the caller decide.

## Summary

Java's exception model separates normal logic from error-handling code, enforces compile-time awareness of checked failures, and guarantees resource cleanup via `try-with-resources`. Mastering these three constructs — `try/catch/finally`, `try-with-resources`, and custom exception classes — is essential before writing any Spring Boot service that touches a database or the file system.
