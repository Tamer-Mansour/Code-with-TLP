# Project: Student Management System (Console)

## Overview

You'll build a **console-based Student Management System (SMS)** in pure Java that persists data to a **MySQL 8** database via JDBC. This is your first end-to-end project: it ties together everything from Java Foundations — classes, collections, exceptions, the `Scanner` — with real persistence so your data survives between runs.

Why it matters: almost every backend system is, at its core, a **CRUD application** (Create, Read, Update, Delete) over a datastore. By building one by hand with JDBC before reaching for Spring, you'll understand exactly what frameworks do for you later — connections, prepared statements, mapping rows to objects, and clean layering.

## Learning Objectives

By the end of this project you will be able to:

- Model a domain entity (`Student`) as a plain Java class (POJO).
- Connect to MySQL from Java using **JDBC** and the MySQL Connector/J driver.
- Write parameterized SQL with `PreparedStatement` to prevent SQL injection.
- Separate concerns using a **DAO (Data Access Object)** layer, a **service** layer, and a console **UI** layer.
- Handle `SQLException` and invalid user input gracefully.
- Drive a menu-based console loop that maps user choices to operations.

## Prerequisites & Setup

You need **JDK 17+**, **MySQL 8**, and the **MySQL Connector/J** JAR on your classpath. Confirm your tools and create the database:

```bash
java -version          # expect 17 or higher
mysql --version        # expect 8.x

# Create the schema
mysql -u root -p -e "CREATE DATABASE sms CHARACTER SET utf8mb4;"
```

Create the table:

```sql
USE sms;

CREATE TABLE students (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100)        NOT NULL,
    email      VARCHAR(150) UNIQUE NOT NULL,
    grade      DECIMAL(4,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Download `mysql-connector-j` (e.g. `mysql-connector-j-8.4.0.jar`) into a `lib/` folder. Compile and run with the driver on the classpath:

```bash
# Windows (note the ; separator)
javac -d out src\com\tlp\sms\*.java
java -cp "out;lib\mysql-connector-j-8.4.0.jar" com.tlp.sms.App
```

## Requirements

The application must let a user, from a text menu:

1. **Add** a new student (name, email, grade).
2. **List** all students in a readable table.
3. **Find** a single student by `id`.
4. **Update** an existing student's grade.
5. **Delete** a student by `id`.
6. **Exit** cleanly.

All data lives in MySQL — restarting the program must show the same students.

## Step-by-Step Tasks

### 1. Model the entity

- [ ] Create `Student` with fields `id`, `name`, `email`, `grade`.
- [ ] Add a constructor, getters, and a `toString()`.

```java
package com.tlp.sms;

public class Student {
    private int id;
    private String name;
    private String email;
    private double grade;

    public Student(int id, String name, String email, double grade) {
        this.id = id; this.name = name; this.email = email; this.grade = grade;
    }
    public int getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public double getGrade() { return grade; }
}
```

### 2. Centralize the connection

- [ ] Create a `Database` helper that returns a `Connection`.
- [ ] Keep credentials in one place so they're easy to change.

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class Database {
    private static final String URL  = "jdbc:mysql://localhost:3306/sms";
    private static final String USER = "root";
    private static final String PASS = "your_password";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASS);
    }
}
```

### 3. Build the DAO (data access)

- [ ] Implement `insert`, `findAll`, `findById`, `updateGrade`, `delete`.
- [ ] Use `PreparedStatement` for every query — never string concatenation.
- [ ] Use try-with-resources so connections close automatically.

```java
public Student insert(Student s) throws SQLException {
    String sql = "INSERT INTO students(name, email, grade) VALUES (?, ?, ?)";
    try (Connection c = Database.getConnection();
         PreparedStatement ps =
             c.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
        ps.setString(1, s.getName());
        ps.setString(2, s.getEmail());
        ps.setDouble(3, s.getGrade());
        ps.executeUpdate();
        try (ResultSet keys = ps.getGeneratedKeys()) {
            int id = keys.next() ? keys.getInt(1) : 0;
            return new Student(id, s.getName(), s.getEmail(), s.getGrade());
        }
    }
}
```

```java
public List<Student> findAll() throws SQLException {
    String sql = "SELECT id, name, email, grade FROM students ORDER BY id";
    List<Student> result = new ArrayList<>();
    try (Connection c = Database.getConnection();
         PreparedStatement ps = c.prepareStatement(sql);
         ResultSet rs = ps.executeQuery()) {
        while (rs.next()) {
            result.add(new Student(
                rs.getInt("id"), rs.getString("name"),
                rs.getString("email"), rs.getDouble("grade")));
        }
    }
    return result;
}
```

### 4. Build the console UI

- [ ] Read input with a single shared `Scanner`.
- [ ] Print a menu, read an `int` choice, and route it.
- [ ] Validate input (reject empty names, bad numbers).

```java
private static void printMenu() {
    System.out.println("""
        === Student Management System ===
        1) Add student
        2) List students
        3) Find by id
        4) Update grade
        5) Delete student
        0) Exit""");
    System.out.print("Choose: ");
}
```

### 5. Wire the main loop

- [ ] Loop until the user picks `0`.
- [ ] Wrap each operation in try/catch for `SQLException`.

```java
public static void main(String[] args) {
    StudentDao dao = new StudentDao();
    Scanner in = new Scanner(System.in);
    while (true) {
        printMenu();
        int choice = Integer.parseInt(in.nextLine().trim());
        try {
            switch (choice) {
                case 1 -> addStudent(in, dao);
                case 2 -> listStudents(dao);
                case 0 -> { System.out.println("Bye!"); return; }
                default -> System.out.println("Unknown option.");
            }
        } catch (SQLException e) {
            System.out.println("Database error: " + e.getMessage());
        }
    }
}
```

Format the list output as an aligned table:

| id | name        | email             | grade |
|----|-------------|-------------------|-------|
| 1  | Sara Ali    | sara@example.com  | 92.50 |
| 2  | Omar Nasser | omar@example.com  | 78.00 |

```java
System.out.printf("%-4d %-15s %-22s %.2f%n",
    s.getId(), s.getName(), s.getEmail(), s.getGrade());
```

## Acceptance Criteria

- [ ] Program compiles with `javac` and runs with the connector on the classpath.
- [ ] Adding a student inserts a row and prints the new generated `id`.
- [ ] Listing shows all students in an aligned table; data persists across restarts.
- [ ] Find-by-id returns the correct student or a clear "not found" message.
- [ ] Updating a grade changes the stored value (verifiable via `SELECT` in MySQL).
- [ ] Deleting removes the row; deleting a missing id reports it without crashing.
- [ ] All SQL uses `PreparedStatement`; no string-concatenated queries.
- [ ] Invalid menu input or a non-numeric grade does not crash the app.

## Stretch Challenges

1. **Search by name** with a `LIKE ?` query (e.g. `WHERE name LIKE ?` bound to `"%term%"`).
2. **Pagination** — add `LIMIT ? OFFSET ?` and let the user page through results.
3. **Transactions** — add a "bulk import" that wraps several inserts in one transaction with `setAutoCommit(false)` and `rollback()` on failure.
4. **Externalize config** — move URL/user/password into a `db.properties` file loaded with `Properties`.
5. **Class statistics** — compute and display the average and highest grade using SQL aggregates (`AVG`, `MAX`).

## Hints

- Wrap `Integer.parseInt(...)` in a try/catch for `NumberFormatException` so a typo in the menu doesn't kill the loop.
- The `UNIQUE` constraint on `email` throws an `SQLIntegrityConstraintViolationException` (a subclass of `SQLException`) on duplicates — catch it to show a friendly "email already exists" message.
- Prefer `executeUpdate()` for INSERT/UPDATE/DELETE (it returns the affected row count — useful for "0 means not found") and `executeQuery()` for SELECT.
- Keep the three layers separate: the DAO never prints, and the UI never writes SQL. This is the same boundary Spring will enforce for you later.
