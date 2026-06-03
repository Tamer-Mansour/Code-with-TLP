# Quiz: MySQL

Test your understanding of relational database design, SQL queries, indexing, transactions, and Spring Boot integration with MySQL covered in this module. Each question has exactly one correct answer.

---

**Q1. Which SQL statement correctly creates a table named `orders` with an auto-incrementing primary key, a non-null `total` column of type `DECIMAL(10,2)`, and a foreign key referencing the `customers` table?**

```sql
CREATE TABLE orders (
    id         INT          NOT NULL AUTO_INCREMENT,
    customer_id INT         NOT NULL,
    total      DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

- [ ] The `AUTO_INCREMENT` keyword is not valid in MySQL 8; use `SERIAL` instead
- [ ] A `FOREIGN KEY` constraint cannot be defined in a `CREATE TABLE` statement; it must be added with `ALTER TABLE`
- [x] The statement is correct: `AUTO_INCREMENT` generates the primary key, `DECIMAL(10,2)` stores monetary values, and the inline `FOREIGN KEY` clause creates a referential integrity constraint
- [ ] `DECIMAL(10,2)` stores a maximum of 10 digits after the decimal point

---

**Q2. You run the following query and receive 0 rows, but you know the data exists:**

```sql
SELECT * FROM products WHERE name = 'Widget Pro';
```

The `name` column is defined as `VARCHAR(100)` with the collation `utf8mb4_bin`. What is the most likely cause?**
- [ ] `VARCHAR` columns cannot be used in `WHERE` clauses without casting
- [x] `utf8mb4_bin` is a binary, case-sensitive collation, so `'Widget Pro'` does not match `'widget pro'` or `'WIDGET PRO'`
- [ ] MySQL 8 requires `LIKE` instead of `=` for string comparisons
- [ ] The query is missing a `LIMIT` clause, which causes MySQL to return no rows by default

---

**Q3. What does the following `EXPLAIN` output indicate about the query's execution?**

```
+----+-------------+----------+------+---------------+------+-------+------+--------+
| id | select_type | table    | type | possible_keys | key  | rows  | Extra       |
+----+-------------+----------+------+---------------+------+-------+------+--------+
|  1 | SIMPLE      | orders   | ALL  | NULL          | NULL | 95000 | Using where |
+----+-------------+----------+------+---------------+------+-------+------+--------+
```

- [ ] MySQL chose the most efficient index for this query
- [ ] The query returns 95 000 rows, which is normal and expected
- [ ] `type: ALL` means MySQL used a full-index scan, which is faster than a range scan
- [x] `type: ALL` and `key: NULL` mean MySQL performed a full table scan across 95 000 rows with no index, indicating an index should be added to the filtered column

---

**Q4. Which isolation level prevents dirty reads and non-repeatable reads but still allows phantom reads?**

| Isolation Level    | Dirty Read | Non-Repeatable Read | Phantom Read |
|--------------------|-----------|---------------------|--------------|
| READ UNCOMMITTED   | Possible  | Possible            | Possible     |
| READ COMMITTED     | Prevented | Possible            | Possible     |
| REPEATABLE READ    | Prevented | Prevented           | Possible     |
| SERIALIZABLE       | Prevented | Prevented           | Prevented    |

- [ ] `READ UNCOMMITTED`
- [ ] `READ COMMITTED`
- [x] `REPEATABLE READ`
- [ ] `SERIALIZABLE`

---

**Q5. A Spring Boot application uses the following `application.properties` snippet:**

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/shopdb?useSSL=false&serverTimezone=UTC
spring.datasource.username=app_user
spring.datasource.password=s3cr3t
spring.jpa.hibernate.ddl-auto=validate
```

What does `ddl-auto=validate` do at application startup?**
- [ ] It drops and recreates all tables on every startup
- [ ] It creates missing tables but never alters or drops existing ones
- [ ] It does nothing; schema management is handled entirely by Hibernate's migration tool
- [x] It compares the entity mappings against the existing database schema and throws an exception if they do not match, without making any schema changes

---

**Q6. You need to return each customer's name alongside the total number of orders they have placed, including customers who have placed zero orders. Which query is correct?**

```sql
-- Option A
SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name;

-- Option B
SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name;
```

- [x] Option A, because `LEFT JOIN` preserves all rows from `customers` and `COUNT(o.id)` returns 0 when no matching order exists
- [ ] Option B, because `INNER JOIN` is always faster and the result is the same
- [ ] Option A, but `COUNT(*)` must be used instead of `COUNT(o.id)` to include zero-order customers
- [ ] Both options return identical results; the join type does not affect the count

---

**Q7. Which statement about MySQL indexes is accurate?**
- [ ] Adding more indexes always improves both read and write performance
- [ ] A composite index on `(last_name, first_name)` is equally efficient for a query filtering only on `first_name`
- [ ] `FULLTEXT` indexes can be used to speed up range queries such as `WHERE price BETWEEN 10 AND 50`
- [x] A composite index on `(last_name, first_name)` supports queries that filter on `last_name` alone or on both columns, but not efficiently on `first_name` alone, due to the leftmost prefix rule

---

**Q8. The following transaction is executed; what is the final value of `balance` for account `id = 1` if the `UPDATE` succeeds but an error occurs before the `COMMIT`?**

```sql
START TRANSACTION;
UPDATE accounts SET balance = balance - 500 WHERE id = 1;
-- application error occurs here
ROLLBACK;
```

- [ ] The balance is permanently decreased by 500 because the `UPDATE` already executed
- [x] The balance is unchanged because `ROLLBACK` undoes all statements in the transaction back to the `START TRANSACTION` point
- [ ] The balance is decreased by 500, and only future transactions see the new value
- [ ] MySQL auto-commits the `UPDATE` immediately, making `ROLLBACK` ineffective

---

**Q9. You define the following JPA entity in a Spring Boot project:**

```java
@Entity
@Table(name = "articles")
public class Article {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 255)
    private String title;

    @Lob
    private String body;

    // getters and setters
}
```

What does `GenerationType.IDENTITY` tell Hibernate to do?**
- [ ] Hibernate generates UUID primary keys in Java before inserting the row
- [ ] Hibernate uses a shared database sequence object across all tables
- [x] Hibernate relies on the database's `AUTO_INCREMENT` column to generate the primary key after each `INSERT`, then reads the generated value back
- [ ] Hibernate assigns primary keys from an in-memory counter that resets on every application restart

---

**Q10. A developer writes this Spring Data JPA repository method:**

```java
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByCategoryAndPricelessThan(String category, BigDecimal maxPrice);
}
```

What SQL does Spring Data JPA derive and execute for this method?**
- [ ] `SELECT * FROM product WHERE category = ? OR price < ?`
- [ ] `SELECT * FROM product WHERE category LIKE ? AND price <= ?`
- [x] `SELECT * FROM product WHERE category = ? AND price < ?`
- [ ] The method name is invalid; Spring Data JPA cannot combine two conditions without a `@Query` annotation
