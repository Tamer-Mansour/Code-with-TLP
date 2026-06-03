# Capstone Project: E-Commerce REST API

## Overview

This capstone ties together everything you've learned in **Spring Boot Mastery**: REST controllers, JPA persistence, validation, exception handling, security, and testing. You'll design and build a production-shaped **E-Commerce REST API** that manages products, customers, shopping carts, and orders.

Why it matters: an e-commerce backend is the canonical "real" Spring Boot project. It forces you to model relationships (one-to-many, many-to-many), enforce business rules (stock cannot go negative), secure endpoints by role, and return clean, predictable JSON. By the end you'll have a portfolio-grade service you can deploy and demo.

## Learning Objectives

- Model a relational domain with **JPA entities** and well-chosen fetch types.
- Expose a clean, versioned REST API using DTOs (never leak entities directly).
- Apply **Bean Validation** and centralized error handling with `@RestControllerAdvice`.
- Secure endpoints with **Spring Security** + JWT and role-based authorization.
- Enforce transactional business logic (stock decrement, order totals).
- Write meaningful **integration tests** with `@SpringBootTest` and Testcontainers (or H2).

## Prerequisites & Setup

- JDK 17+ and Maven 3.9+
- PostgreSQL 15+ (or use the included Docker command)
- An HTTP client (curl, HTTPie, or Postman)

Generate the project with Spring Initializr, then start a database:

```bash
# Scaffold the project
curl https://start.spring.io/starter.zip \
  -d dependencies=web,data-jpa,validation,security,postgresql,lombok \
  -d type=maven-project -d javaVersion=17 \
  -d groupId=com.tlp -d artifactId=ecommerce-api \
  -d name=ecommerce-api -o ecommerce-api.zip
unzip ecommerce-api.zip -d ecommerce-api

# Run PostgreSQL
docker run --name ecom-db -e POSTGRES_DB=ecom \
  -e POSTGRES_PASSWORD=secret -p 5432:5432 -d postgres:15
```

`src/main/resources/application.properties`:

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/ecom
spring.datasource.username=postgres
spring.datasource.password=secret
spring.jpa.hibernate.ddl-auto=update
spring.jpa.open-in-view=false
app.jwt.secret=change-me-to-a-32-byte-minimum-secret-key
app.jwt.expiration-ms=3600000
```

## Requirements

| Area | Functional spec |
|------|-----------------|
| Products | CRUD products; each has name, description, price (BigDecimal), and stock quantity. |
| Auth | Register/login; JWT issued on login; `USER` and `ADMIN` roles. |
| Catalog | Anyone can list/search products; only `ADMIN` can create/update/delete. |
| Cart | A logged-in `USER` adds items to a cart and adjusts quantities. |
| Orders | Checkout converts the cart to an order, decrements stock atomically, and computes the total. |
| Errors | All failures return a consistent JSON error body with proper HTTP status. |

## Step-by-Step Tasks

### 1. Model the domain

- [ ] Create `Product`, `User`, `CartItem`, `Order`, and `OrderLine` entities.
- [ ] Use `BigDecimal` for money and a `@Version` column on `Product` for optimistic locking.

```java
@Entity
@Table(name = "products")
public class Product {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    private String description;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal price;

    @Column(nullable = false)
    private int stock;

    @Version
    private Long version;
    // getters & setters
}
```

### 2. Repositories & DTOs

- [ ] Create Spring Data `JpaRepository` interfaces for each aggregate root.
- [ ] Add a search query and define request/response records so entities never hit the wire.

```java
public interface ProductRepository extends JpaRepository<Product, Long> {
    Page<Product> findByNameContainingIgnoreCase(String q, Pageable page);
}

public record ProductResponse(Long id, String name, String description,
                              BigDecimal price, int stock) {}

public record ProductRequest(
        @NotBlank String name,
        String description,
        @NotNull @DecimalMin("0.0") BigDecimal price,
        @Min(0) int stock) {}
```

### 3. Build the catalog controller

- [ ] Implement public read endpoints and admin-only write endpoints.
- [ ] Return `201 Created` with a `Location` header on creation.

```java
@RestController
@RequestMapping("/api/v1/products")
public class ProductController {
    private final ProductService service;

    public ProductController(ProductService service) { this.service = service; }

    @GetMapping
    public Page<ProductResponse> list(@RequestParam(defaultValue = "") String q, Pageable page) {
        return service.search(q, page);
    }

    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ProductResponse> create(@Valid @RequestBody ProductRequest req) {
        ProductResponse created = service.create(req);
        return ResponseEntity.created(URI.create("/api/v1/products/" + created.id())).body(created);
    }
}
```

### 4. Security & JWT

- [ ] Configure a `SecurityFilterChain` (stateless), a `BCryptPasswordEncoder`, and a JWT filter.
- [ ] Permit `/api/v1/auth/**` and `GET /api/v1/products/**`; secure the rest.

```java
@Bean
SecurityFilterChain chain(HttpSecurity http, JwtFilter jwtFilter) throws Exception {
    http.csrf(csrf -> csrf.disable())
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .authorizeHttpRequests(a -> a
            .requestMatchers("/api/v1/auth/**").permitAll()
            .requestMatchers(HttpMethod.GET, "/api/v1/products/**").permitAll()
            .anyRequest().authenticated())
        .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
    return http.build();
}
```

### 5. Cart & checkout (transactional)

- [ ] Implement add-to-cart and a `checkout` method that runs in one transaction.
- [ ] Decrement stock and reject checkout if any item is out of stock.

```java
@Transactional
public OrderResponse checkout(User user) {
    List<CartItem> items = cartRepo.findByUser(user);
    if (items.isEmpty()) throw new BadRequestException("Cart is empty");

    Order order = new Order(user);
    for (CartItem item : items) {
        Product p = item.getProduct();
        if (p.getStock() < item.getQuantity())
            throw new BadRequestException("Out of stock: " + p.getName());
        p.setStock(p.getStock() - item.getQuantity());
        order.addLine(p, item.getQuantity(), p.getPrice());
    }
    order.recalculateTotal();
    cartRepo.deleteAll(items);
    return OrderMapper.toResponse(orderRepo.save(order));
}
```

### 6. Global error handling

- [ ] Add a `@RestControllerAdvice` mapping exceptions to a uniform body.

```java
@RestControllerAdvice
public class ApiExceptionHandler {
    public record ApiError(int status, String message, Instant timestamp) {}

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiError> onValidation(MethodArgumentNotValidException ex) {
        String msg = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return ResponseEntity.badRequest().body(new ApiError(400, msg, Instant.now()));
    }
}
```

### 7. Tests

- [ ] Write a `@SpringBootTest` that registers a user, logs in, and checks out.
- [ ] Assert stock is decremented and a second checkout of the same out-of-stock item returns `400`.

## Acceptance Criteria

- [ ] `GET /api/v1/products` returns a paginated list without authentication.
- [ ] A non-admin token cannot `POST /api/v1/products` (returns `403`).
- [ ] Invalid product payloads return `400` with field-level messages.
- [ ] Checkout decrements `Product.stock` and computes the correct order total.
- [ ] Concurrent checkouts cannot drive stock below zero (optimistic locking or guarded transaction).
- [ ] All endpoints return JSON; no JPA entity is serialized directly.
- [ ] `mvn test` passes with at least one happy-path and one failure-path integration test.

## Stretch Challenges

1. Add **pagination + sorting** to orders and a customer order-history endpoint.
2. Introduce **idempotency keys** on checkout so a retried request doesn't create duplicate orders.
3. Emit a domain event (`ApplicationEventPublisher`) on order placement and log it via a listener.
4. Add **OpenAPI/Swagger** docs with `springdoc-openapi-starter-webmvc-ui`.
5. Containerize the app and database with a `docker-compose.yml` and a multi-stage `Dockerfile`.

## Hints

- Keep services thin but make them the *only* place that touches repositories and `@Transactional`.
- Money: never use `double`. `BigDecimal` with `precision`/`scale` avoids rounding bugs.
- For JWT, parse and validate the token once in a `OncePerRequestFilter`, then set the `SecurityContext`.
- If you hit `LazyInitializationException`, map to DTOs inside the transaction rather than enabling open-in-view.
- Test the stock race with two threads calling `checkout`; `@Version` will throw `OptimisticLockException` you can translate to `409 Conflict`.
