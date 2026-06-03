# Quiz: Spring Data JPA

Test your understanding of JPA entities, Spring Data repositories, JPQL, derived query methods, transactions, pagination, and Spring Boot auto-configuration for data persistence.

---

**Q1. Which annotation marks a Java class as a JPA entity that maps to a database table?**
- [ ] `@Table`
- [ ] `@Column`
- [x] `@Entity`
- [ ] `@Persistent`

> `@Entity` (from `jakarta.persistence`) is required on every class that JPA should manage. `@Table` is optional and lets you override the default table name. Without `@Entity` the class is ignored by the JPA provider (Hibernate).

---

**Q2. What is the correct way to declare a surrogate primary key that the database auto-generates in a JPA entity?**

```java
@Entity
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
}
```

- [ ] Annotate the field with `@PrimaryKey` and `@AutoIncrement`.
- [ ] Annotate the field with `@Id` only — Spring Data generates the value automatically.
- [ ] Annotate the field with `@GeneratedValue` alone; `@Id` is inferred.
- [x] Annotate the field with both `@Id` and `@GeneratedValue(strategy = GenerationType.IDENTITY)`.

> `@Id` designates the primary key field; `@GeneratedValue` specifies how the key is produced. `IDENTITY` delegates generation to the database column's auto-increment feature. Other strategies include `SEQUENCE` (recommended for PostgreSQL) and `UUID`.

---

**Q3. You extend `JpaRepository<Product, Long>` in your repository interface. Which method do you call to retrieve an `Optional<Product>` by its primary key?**
- [ ] `get(id)`
- [ ] `load(id)`
- [x] `findById(id)`
- [ ] `getOne(id)`

> `findById` returns `Optional<T>`, making null-safety explicit. `getOne` / `getReferenceById` returns a lazy proxy and throws `EntityNotFoundException` on access if the entity does not exist — it does not wrap the result in an `Optional`.

---

**Q4. What does the following Spring Data derived query method name resolve to?**

```java
List<Order> findByCustomerLastNameAndStatusOrderByCreatedAtDesc(String lastName, String status);
```

- [ ] A native SQL query — Spring Data passes the method name directly to the database.
- [ ] It causes a compilation error because the method name is too long.
- [ ] A stored procedure call named `find_by_customer_last_name_and_status`.
- [x] A JPQL query that filters on `customer.lastName` and `status`, ordering results by `createdAt` descending.

> Spring Data parses method names at application startup and generates JPQL. Keywords such as `And`, `Or`, `OrderBy`, `Desc`, `Like`, and `Between` map directly to JPQL clauses. If parsing fails, startup throws a `QueryCreationException`.

---

**Q5. You need a custom query to count active products by category. Which approach is correct?**

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    // Option A
    @Query("SELECT COUNT(p) FROM Product p WHERE p.category = :cat AND p.active = true")
    long countActiveByCategoryJpql(@Param("cat") String category);

    // Option B
    @Query(value = "SELECT COUNT(*) FROM products WHERE category = :cat AND active = true",
           nativeQuery = true)
    long countActiveByCategoryNative(@Param("cat") String category);
}
```

- [ ] Only Option A compiles; `nativeQuery = true` is not a valid attribute of `@Query`.
- [ ] Only Option B is correct; JPQL cannot use aggregate functions like `COUNT`.
- [ ] Neither option is valid — custom queries must be placed in a separate `@Service` class.
- [x] Both options are valid; Option A uses JPQL (entity names and fields), Option B uses native SQL (table and column names).

---

**Q6. Which Spring Boot property sets the Hibernate DDL auto-generation strategy so that the schema is created on startup and dropped on shutdown — useful for in-memory databases during testing?**

```properties
spring.jpa.hibernate.ddl-auto=???
```

| Value | Behaviour |
|---|---|
| `none` | No DDL action |
| `validate` | Validate schema; throw if mismatch |
| `update` | Alter existing schema to match entities |
| `create` | Drop then re-create schema on startup |
| `create-drop` | Create on startup, drop on shutdown |

- [ ] `spring.jpa.hibernate.ddl-auto=create`
- [x] `spring.jpa.hibernate.ddl-auto=create-drop`
- [ ] `spring.jpa.hibernate.ddl-auto=update`
- [ ] `spring.jpa.hibernate.ddl-auto=validate`

---

**Q7. A service method updates a `User` entity. Which annotation ensures the operation runs inside a database transaction, and where should it be placed?**

```java
@Service
public class UserService {

    // Which annotation goes here?
    public void updateEmail(Long userId, String newEmail) {
        User user = userRepository.findById(userId).orElseThrow();
        user.setEmail(newEmail);
        // No explicit save() needed — dirty checking flushes the change on commit
    }
}
```

- [ ] `@Transactional` from `jakarta.persistence` placed on the repository interface.
- [ ] `@EnableTransactionManagement` placed on the service method.
- [ ] `@Commit` placed on the service method.
- [x] `@Transactional` from `org.springframework.transaction.annotation` placed on the service method (or class).

> Spring's `@Transactional` wraps the method in a proxy that opens a transaction before the call and commits (or rolls back on unchecked exceptions) after it returns. Dirty checking then automatically flushes any changes made to managed entities within that transaction.

---

**Q8. You want to return a page of `Product` records sorted by price descending, 10 items per page. Which method call is correct?**

```java
// Repository
Page<Product> findByActiveTrue(Pageable pageable);

// Service call
Pageable page = PageRequest.of(0, 10, Sort.by("price").descending());
Page<Product> result = productRepository.findByActiveTrue(page);
```

- [ ] `PageRequest.of(1, 10)` — pages are 1-indexed in Spring Data.
- [ ] `Sort.by("price").desc()` — the method is `desc()`, not `descending()`.
- [ ] `findByActiveTrue` does not support `Pageable`; you must use `@Query` for paginated queries.
- [x] The code is correct — `PageRequest.of(0, 10, Sort.by("price").descending())` creates a zero-indexed first page of 10 items sorted by `price` descending.

> `PageRequest.of(pageNumber, pageSize, sort)` is zero-indexed. The returned `Page<T>` exposes `getContent()`, `getTotalElements()`, `getTotalPages()`, and navigation helpers like `hasNext()`.

---

**Q9. What is the "N+1 select problem" in JPA, and which fetch strategy prevents it when loading a `Post` with its list of `Comment` entities?**
- [ ] Spring executes N queries for 1 entity because the entity has N fields; solved by `@Column(lazy = true)`.
- [ ] The persistence context keeps N+1 copies of each entity in memory; solved by calling `entityManager.clear()`.
- [x] Loading N parent entities each triggers an additional query to fetch their child collection, totalling N+1 queries; solved by using a `JOIN FETCH` in JPQL or `@EntityGraph` to load children in a single query.
- [ ] Hibernate logs N+1 warnings when a table has more than one index; solved by removing redundant indexes.

> Example fix using `@Query`:
> ```java
> @Query("SELECT p FROM Post p JOIN FETCH p.comments WHERE p.id = :id")
> Optional<Post> findByIdWithComments(@Param("id") Long id);
> ```
> Or with `@EntityGraph`:
> ```java
> @EntityGraph(attributePaths = "comments")
> Optional<Post> findById(Long id);
> ```

---

**Q10. Which relationship mapping annotation, combined with `CascadeType.ALL` and `orphanRemoval = true`, ensures that child `Address` records are automatically deleted when they are removed from the parent `Customer`'s list?**

```java
@Entity
public class Customer {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @???
    @JoinColumn(name = "customer_id")
    private List<Address> addresses = new ArrayList<>();
}
```

- [ ] `@ManyToMany(cascade = CascadeType.ALL, orphanRemoval = true)`
- [ ] `@ManyToOne(cascade = CascadeType.ALL, orphanRemoval = true)`
- [ ] `@OneToOne(cascade = CascadeType.ALL, orphanRemoval = true)`
- [x] `@OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)`

> `@OneToMany` models a one-to-many relationship. `CascadeType.ALL` propagates all lifecycle operations (persist, merge, remove) from parent to children. `orphanRemoval = true` additionally removes a child row from the database when the child object is removed from the parent collection — even without an explicit `remove()` call on the entity manager.
