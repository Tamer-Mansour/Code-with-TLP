# SELECT, WHERE, ORDER BY

Reading data is the most common database operation you will perform. The `SELECT` statement retrieves rows from one or more tables; `WHERE` filters them; `ORDER BY` sorts them. Mastering these three clauses is the foundation of every database-backed feature you will build with Spring Data JPA or plain JDBC.

## The SELECT Statement

The minimal `SELECT` picks columns from a table:

```sql
SELECT column1, column2
FROM table_name;
```

Use `*` to fetch every column, but prefer explicit column names in production — it avoids fetching data you do not need and makes queries self-documenting.

Assume the following table used in all examples below:

```sql
CREATE TABLE product (
    id          INT           NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)  NOT NULL,
    category    VARCHAR(50)   NOT NULL,
    price       DECIMAL(10,2) NOT NULL,
    stock       INT           NOT NULL DEFAULT 0,
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Selecting specific columns

```sql
SELECT id, name, price
FROM product;
```

### Selecting all columns

```sql
SELECT *
FROM product;
```

### Column aliases

Use `AS` to rename a column in the result set — useful when the application reads result-set labels by name:

```sql
SELECT name AS product_name, price AS unit_price
FROM product;
```

## Filtering Rows with WHERE

`WHERE` evaluates a boolean expression for every row; only rows for which the expression is `TRUE` are returned.

```sql
SELECT id, name, price
FROM product
WHERE category = 'Electronics';
```

### Comparison and logical operators

| Operator | Meaning | Example |
|---|---|---|
| `=` | Equal | `price = 49.99` |
| `<>` or `!=` | Not equal | `category <> 'Books'` |
| `>` / `<` | Greater / less than | `price > 100` |
| `>=` / `<=` | Greater or equal / less or equal | `stock <= 5` |
| `AND` | Both conditions true | `price > 10 AND stock > 0` |
| `OR` | Either condition true | `category = 'Books' OR category = 'Music'` |
| `NOT` | Negation | `NOT (price < 1)` |
| `BETWEEN` | Inclusive range | `price BETWEEN 20 AND 60` |
| `IN` | Matches any value in a list | `category IN ('Electronics', 'Gadgets')` |
| `LIKE` | Pattern match | `name LIKE 'Java%'` |
| `IS NULL` | Value is missing | `description IS NULL` |

### Realistic multi-condition query

```sql
SELECT id, name, category, price, stock
FROM product
WHERE category IN ('Electronics', 'Gadgets')
  AND price BETWEEN 20.00 AND 200.00
  AND stock > 0;
```

### Pattern matching with LIKE

`%` matches any sequence of characters; `_` matches exactly one character.

```sql
-- Products whose name starts with "Spring"
SELECT name FROM product WHERE name LIKE 'Spring%';

-- Products with exactly 5-character names
SELECT name FROM product WHERE name LIKE '_____';
```

## Sorting Results with ORDER BY

`ORDER BY` sorts the result set by one or more columns. The default direction is ascending (`ASC`); use `DESC` to reverse it.

```sql
SELECT id, name, price
FROM product
ORDER BY price ASC;
```

### Multi-column sort

Rows are first sorted by `category`, then within each category by `price` descending:

```sql
SELECT id, name, category, price
FROM product
WHERE stock > 0
ORDER BY category ASC, price DESC;
```

### Sorting by alias or expression

MySQL allows sorting by a column alias defined in `SELECT`:

```sql
SELECT name, price * 1.2 AS price_with_tax
FROM product
ORDER BY price_with_tax DESC;
```

## Combining All Three Clauses

The canonical query structure — and the order MySQL evaluates them — is:

```sql
SELECT id, name, category, price        -- 3. choose columns to return
FROM product                            -- 1. identify the table
WHERE category = 'Electronics'          -- 2. filter rows
  AND stock > 0
ORDER BY price ASC;                     -- 4. sort the remaining rows
```

A concrete realistic example — "show the top 5 cheapest in-stock electronics":

```sql
SELECT id, name, price, stock
FROM product
WHERE category = 'Electronics'
  AND stock > 0
ORDER BY price ASC
LIMIT 5;
```

## Accessing These Queries from Java (JDBC)

When you need raw SQL inside a Spring Boot service, use `JdbcTemplate`:

```java
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Map;

@Repository
public class ProductRepository {

    private final JdbcTemplate jdbc;

    public ProductRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public List<Map<String, Object>> findCheapInStockElectronics() {
        String sql = """
                SELECT id, name, price, stock
                FROM product
                WHERE category = 'Electronics'
                  AND stock > 0
                ORDER BY price ASC
                LIMIT 5
                """;
        return jdbc.queryForList(sql);
    }

    public List<Map<String, Object>> findByCategory(String category) {
        String sql = """
                SELECT id, name, price
                FROM product
                WHERE category = ?
                ORDER BY price ASC
                """;
        return jdbc.queryForList(sql, category);          // parameterised — no SQL injection
    }
}
```

Always use `?` placeholders (or named parameters) rather than string concatenation — this prevents SQL injection.

## Common Mistakes and Best Practices

- **`SELECT *` in production code** — fetches every column on every call; use explicit column lists to reduce network traffic and avoid surprises when the schema changes.
- **Forgetting `WHERE` on an `UPDATE` or `DELETE`** — always test your `WHERE` clause with a `SELECT` first before modifying data.
- **Case sensitivity** — MySQL string comparisons on `utf8mb4_general_ci` collations are case-insensitive by default, but rely on this consciously; use `BINARY` when exact case matters.
- **NULL comparisons** — `WHERE column = NULL` never matches any row; always use `IS NULL` or `IS NOT NULL`.
- **Implicit type coercion** — comparing a `VARCHAR` column to a number (`WHERE id = '5'`) works but forces a full table scan; match the data types of your predicates to the column types.
- **Missing index on WHERE columns** — for large tables, ensure frequently filtered columns are indexed (`CREATE INDEX idx_category ON product(category)`).

## Summary

`SELECT` chooses which columns to return, `WHERE` narrows the rows to only those matching your criteria, and `ORDER BY` arranges the result in a meaningful sequence. Together they form the read backbone of every SQL query you will write in a Java/Spring application.
