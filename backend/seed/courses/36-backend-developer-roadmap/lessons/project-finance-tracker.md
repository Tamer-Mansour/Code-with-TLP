# Project: Personal Finance Tracker (Console)

## Overview

In this project you'll build a **Personal Finance Tracker** that runs entirely in the terminal. The user records income and expense transactions, lists them, filters by category, and sees a running balance and a per-category summary. Data is stored in a **MySQL 8** database through plain **JDBC** — no Spring, no ORM.

This is your first end-to-end Java application. It pulls together everything from the *Java Foundations* module: classes and enums, collections, exception handling, a clean menu loop, and your first taste of talking to a real database with SQL and `PreparedStatement`. The layered structure you build here (model → repository → service → console UI) is exactly the shape you'll keep using when you graduate to Spring later in the roadmap.

## Learning Objectives

By the end of this project you will be able to:

- Model a small domain with Java classes and an `enum`.
- Read and validate user input with `Scanner` in a robust menu loop.
- Connect to MySQL from Java using JDBC and the MySQL Connector/J driver.
- Run parameterized queries safely with `PreparedStatement` (no SQL injection).
- Separate concerns across model, repository, service, and UI layers.
- Use `BigDecimal` for money and handle errors gracefully.

## Prerequisites & Setup

You need:

- **JDK 17+** (`java -version` reports 17 or higher)
- **MySQL 8** running locally (`mysql --version`)
- The **MySQL Connector/J** JAR on your classpath

Create the database and table:

```sql
CREATE DATABASE IF NOT EXISTS finance_tracker;
USE finance_tracker;

CREATE TABLE transactions (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255)   NOT NULL,
    amount      DECIMAL(12,2)  NOT NULL,
    type        ENUM('INCOME','EXPENSE') NOT NULL,
    category    VARCHAR(100)   NOT NULL,
    created_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

Download the driver and compile/run from the command line:

```bash
# Place mysql-connector-j-8.4.0.jar in a lib/ folder
javac -cp "lib/*" -d out src/com/tlp/finance/*.java

# Linux/macOS classpath uses ':', Windows uses ';'
java -cp "out:lib/*" com.tlp.finance.App
```

## Requirements

| # | Capability | Menu option |
|---|------------|-------------|
| 1 | Add an income transaction | `1` |
| 2 | Add an expense transaction | `2` |
| 3 | List all transactions (newest first) | `3` |
| 4 | Show summary: total income, total expense, balance | `4` |
| 5 | Show totals grouped by category | `5` |
| 6 | Exit | `0` |

Rules:

- `amount` must be a positive number; reject anything else and re-prompt.
- `description` and `category` must not be blank.
- Balance = total income − total expense.
- All money is handled with `BigDecimal` — never `double`.

## Step-by-Step Tasks

### 1. Model the domain

- [ ] Create a `TransactionType` enum with `INCOME` and `EXPENSE`.
- [ ] Create a `Transaction` class with `id`, `description`, `amount`, `type`, `category`, `createdAt`.

```java
package com.tlp.finance;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public enum TransactionType { INCOME, EXPENSE }

public class Transaction {
    private Long id;
    private final String description;
    private final BigDecimal amount;
    private final TransactionType type;
    private final String category;
    private final LocalDateTime createdAt;

    public Transaction(String description, BigDecimal amount,
                       TransactionType type, String category) {
        this.description = description;
        this.amount = amount;
        this.type = type;
        this.category = category;
        this.createdAt = LocalDateTime.now();
    }
    // getters; setId(...)
}
```

### 2. Create a JDBC connection helper

- [ ] Centralize the JDBC URL, user, and password in one place.
- [ ] Hand out `Connection` objects via `DriverManager`.

```java
package com.tlp.finance;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class Database {
    private static final String URL =
        "jdbc:mysql://localhost:3306/finance_tracker";
    private static final String USER = "root";
    private static final String PASSWORD = "your_password";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}
```

### 3. Build the repository (data access)

- [ ] Implement `save(Transaction)` using a `PreparedStatement`.
- [ ] Implement `findAll()` ordered by `created_at DESC`.
- [ ] Use try-with-resources so connections always close.

```java
public Transaction save(Transaction t) {
    String sql = """
        INSERT INTO transactions (description, amount, type, category)
        VALUES (?, ?, ?, ?)""";
    try (Connection c = Database.getConnection();
         PreparedStatement ps =
             c.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
        ps.setString(1, t.getDescription());
        ps.setBigDecimal(2, t.getAmount());
        ps.setString(3, t.getType().name());
        ps.setString(4, t.getCategory());
        ps.executeUpdate();
        try (ResultSet keys = ps.getGeneratedKeys()) {
            if (keys.next()) t.setId(keys.getLong(1));
        }
        return t;
    } catch (SQLException e) {
        throw new RuntimeException("Failed to save transaction", e);
    }
}
```

### 4. Add the service layer

- [ ] Validate input before persisting.
- [ ] Compute the balance and the per-category totals.

```java
public Map<String, BigDecimal> totalsByCategory() {
    Map<String, BigDecimal> totals = new LinkedHashMap<>();
    for (Transaction t : repository.findAll()) {
        BigDecimal signed = t.getType() == TransactionType.EXPENSE
                ? t.getAmount().negate() : t.getAmount();
        totals.merge(t.getCategory(), signed, BigDecimal::add);
    }
    return totals;
}
```

### 5. Build the console menu loop

- [ ] Print the menu, read a choice, dispatch with a `switch`.
- [ ] Re-prompt on bad input instead of crashing.

```java
Scanner in = new Scanner(System.in);
boolean running = true;
while (running) {
    System.out.print("""
        \n=== Finance Tracker ===
        1) Add income   2) Add expense
        3) List         4) Summary
        5) By category  0) Exit
        > """);
    switch (in.nextLine().trim()) {
        case "1" -> ui.addTransaction(TransactionType.INCOME);
        case "2" -> ui.addTransaction(TransactionType.EXPENSE);
        case "3" -> ui.listAll();
        case "4" -> ui.printSummary();
        case "5" -> ui.printByCategory();
        case "0" -> running = false;
        default  -> System.out.println("Unknown option.");
    }
}
```

### 6. Run and verify manually

```bash
java -cp "out:lib/*" com.tlp.finance.App
# Add a few income/expense rows, then choose Summary
```

## Acceptance Criteria

- [ ] The app connects to MySQL and survives a restart with data intact.
- [ ] Adding income and expense persists a row to the `transactions` table.
- [ ] Listing shows transactions newest-first with id, type, amount, category.
- [ ] Summary prints total income, total expense, and a correct balance.
- [ ] Category totals are grouped correctly (expenses reduce a category total).
- [ ] All SQL uses `PreparedStatement` with `?` placeholders.
- [ ] Invalid amounts (negative, zero, non-numeric) and blank text are rejected with a re-prompt, not a crash.
- [ ] `BigDecimal` is used for every money value.

## Stretch Challenges

1. Add a **delete by id** option and a **search by description** (`WHERE description LIKE ?`).
2. Add a **date-range filter** on the summary using `created_at BETWEEN ? AND ?`.
3. **Export** all transactions to a CSV file using `BufferedWriter`.
4. Move credentials into an **`application.properties`** file loaded with `Properties` instead of hard-coding them.
5. Wrap multi-step writes in a **transaction** (`conn.setAutoCommit(false)` / `commit` / `rollback`).

## Hints

- Read whole lines with `Scanner.nextLine()` and parse yourself; mixing `nextInt()` and `nextLine()` leaves a dangling newline that bites beginners.
- Parse money with `new BigDecimal(text)` and compare with `.compareTo(BigDecimal.ZERO) > 0` — never `==`.
- Store the enum as `t.getType().name()` and read it back with `TransactionType.valueOf(rs.getString("type"))`.
- Always use try-with-resources for `Connection`, `PreparedStatement`, and `ResultSet` so they close even on error.
- If you get `No suitable driver`, the Connector/J JAR isn't on your classpath — check the `-cp` argument.
