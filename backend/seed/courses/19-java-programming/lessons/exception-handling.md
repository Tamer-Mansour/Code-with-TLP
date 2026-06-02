# Exception Handling

Java uses **checked** and **unchecked** exceptions to represent error conditions. Understanding the difference and knowing when to catch vs. propagate is essential to writing robust Java.

## The exception hierarchy

```
Throwable
├── Error          (JVM-level, do not catch: OutOfMemoryError, StackOverflowError)
└── Exception
    ├── IOException           (checked)
    ├── SQLException          (checked)
    ├── RuntimeException      (unchecked)
    │   ├── NullPointerException
    │   ├── IllegalArgumentException
    │   ├── IndexOutOfBoundsException
    │   └── ...
    └── ...
```

- **Checked exceptions** must be declared in a method signature (`throws`) or caught. The compiler enforces this.
- **Unchecked exceptions** (`RuntimeException` and its subclasses) do not need to be declared.

## try-catch-finally

```java
try {
    String s = readFile("data.txt");    // may throw IOException
    int n = Integer.parseInt(s.trim()); // may throw NumberFormatException
    System.out.println(n * 2);
} catch (IOException e) {
    System.err.println("Cannot read file: " + e.getMessage());
} catch (NumberFormatException e) {
    System.err.println("Bad number: " + e.getMessage());
} finally {
    System.out.println("Always runs — good for cleanup");
}
```

Catch the **most specific** exception first.

## Multi-catch (Java 7+)

```java
try {
    // ...
} catch (IOException | SQLException e) {
    log.error("Data access failed", e);
    throw new RuntimeException("Storage error", e);  // re-wrap
}
```

## try-with-resources (Java 7+)

Automatically closes anything that implements `AutoCloseable`:

```java
try (BufferedReader reader = new BufferedReader(new FileReader("file.txt"));
     Connection conn = dataSource.getConnection()) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
}
// reader and conn are closed even if an exception occurs
```

Always prefer try-with-resources over manually closing in `finally`.

## Throwing exceptions

```java
public int divide(int a, int b) {
    if (b == 0) {
        throw new IllegalArgumentException("Divisor must not be zero");
    }
    return a / b;
}
```

## Custom exceptions

```java
// Checked custom exception
public class InsufficientFundsException extends Exception {
    private final double amount;

    public InsufficientFundsException(double amount) {
        super("Insufficient funds: need " + amount + " more");
        this.amount = amount;
    }

    public double getAmount() { return amount; }
}

// Unchecked custom exception
public class ProductNotFoundException extends RuntimeException {
    public ProductNotFoundException(long id) {
        super("Product not found: " + id);
    }
}
```

## Exception chaining

Preserve the original cause when re-throwing:

```java
try {
    // ...
} catch (SQLException e) {
    throw new RuntimeException("DB operation failed", e); // e is the cause
}
```

Retrieve with `e.getCause()`.

## Best practices

| Practice | Rationale |
|----------|-----------|
| Catch specific types, not `Exception` or `Throwable` | Avoids hiding bugs |
| Never swallow exceptions silently (`catch (e) {}`) | Bugs become invisible |
| Log with stack trace (`log.error("msg", e)`) | Preserves diagnostics |
| Prefer unchecked for programming errors | Checked exceptions for recoverable I/O |
| Use try-with-resources for `Closeable` objects | Prevents resource leaks |
| Don't use exceptions for flow control | Performance and readability cost |

## Java 9 `Throwable.getMessage()` and stack walking

```java
// Print only the relevant frames (Java 9+ StackWalker)
StackWalker.getInstance().forEach(frame ->
    System.out.println(frame.getClassName() + "." + frame.getMethodName()));
```
