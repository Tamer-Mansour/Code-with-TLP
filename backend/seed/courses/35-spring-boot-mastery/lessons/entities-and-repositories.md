# Entities and Spring Data Repositories

Spring Data JPA is Spring Boot's answer to boilerplate-heavy data access code. It sits on top of JPA (Jakarta Persistence API) and Hibernate, letting you map Java classes to database tables and perform CRUD operations with almost no SQL.

## JPA Entities

An **entity** is a plain Java class annotated with `@Entity`. Each instance maps to one row in the corresponding table.

```java
package com.codewithtle.demo.model;

import jakarta.persistence.*;

@Entity
@Table(name = "products")
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 120)
    private String name;

    @Column(nullable = false)
    private Double price;

    // JPA requires a no-arg constructor
    protected Product() {}

    public Product(String name, Double price) {
        this.name = name;
        this.price = price;
    }

    // getters and setters omitted for brevity
}
```

Key annotations and what they do:

| Annotation | Purpose |
|---|---|
| `@Entity` | Marks the class as a JPA-managed entity |
| `@Table(name = "...")` | Maps the class to a specific table name (optional — defaults to class name) |
| `@Id` | Designates the primary key field |
| `@GeneratedValue` | Delegates key generation to the database (`IDENTITY`) or a sequence |
| `@Column` | Customises the column name, nullability, length, or uniqueness |

Hibernate reads these annotations at startup and generates the DDL (or validates the schema) automatically based on your `spring.jpa.hibernate.ddl-auto` setting.

## Spring Data Repositories

Instead of writing an `EntityManager` or boilerplate DAO classes, you declare an interface that extends one of Spring Data's repository interfaces.

```java
package com.codewithtle.demo.repository;

import com.codewithtle.demo.model.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    // Derived query — Spring generates the SQL automatically
    List<Product> findByNameContainingIgnoreCase(String keyword);

    // Custom JPQL query
    @org.springframework.data.jpa.repository.Query(
        "SELECT p FROM Product p WHERE p.price < :maxPrice ORDER BY p.price ASC"
    )
    List<Product> findCheaperThan(@org.springframework.data.repository.query.Param("maxPrice") Double maxPrice);
}
```

`JpaRepository<Product, Long>` provides:

- `save(entity)` — insert or update
- `findById(id)` — returns `Optional<Product>`
- `findAll()` — returns all rows
- `deleteById(id)` — delete by primary key
- `count()`, `existsById(id)`, pagination, sorting — and more

Spring Boot auto-detects your repository interfaces at startup (thanks to `@EnableJpaRepositories`, which Boot applies automatically) and creates proxy implementations at runtime — no class to write.

## Using the Repository in a Service

```java
package com.codewithtle.demo.service;

import com.codewithtle.demo.model.Product;
import com.codewithtle.demo.repository.ProductRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
public class ProductService {

    private final ProductRepository repo;

    public ProductService(ProductRepository repo) {
        this.repo = repo;
    }

    public Product create(String name, Double price) {
        return repo.save(new Product(name, price));
    }

    public List<Product> search(String keyword) {
        return repo.findByNameContainingIgnoreCase(keyword);
    }
}
```

Annotating the service with `@Transactional` ensures each method runs inside a database transaction that is committed on success and rolled back on any unchecked exception.

## Required `application.properties` Configuration

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/demo_db
spring.datasource.username=root
spring.datasource.password=secret
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

`ddl-auto=update` adds missing columns and tables without dropping existing data — useful during development. Use `validate` or `none` in production.

## Common Mistakes

- **Missing no-arg constructor** — JPA instantiates entities reflectively; without a no-arg constructor you get an `InstantiationException` at runtime.
- **Bidirectional relationships without `mappedBy`** — omitting `mappedBy` on the inverse side creates a spurious join table.
- **Fetching large associations eagerly** — `@OneToMany` defaults to `LAZY`; switching to `EAGER` on a large collection causes N+1 queries. Use `@EntityGraph` or a JPQL `JOIN FETCH` instead.
- **Calling repository methods outside a transaction** — modifying a managed entity outside a transactional context silently does nothing; always annotate your service layer.

## Summary

Annotate your domain class with `@Entity` and `@Id`, extend `JpaRepository` in an interface, and Spring Boot wires everything together — giving you a full persistence layer with zero boilerplate SQL.
