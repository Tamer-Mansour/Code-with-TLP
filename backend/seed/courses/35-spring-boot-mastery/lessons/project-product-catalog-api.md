# Project: Product Catalog API

## Overview

In this capstone project you'll build a production-style **Product Catalog REST API** with Spring Boot 3 and Java 17+. The service exposes CRUD endpoints for products, organizes them into categories, supports paginated search, validates input, and returns clean, consistent JSON error responses.

This project ties together everything from the *Building REST APIs* module: controllers, DTOs, persistence with Spring Data JPA, bean validation, exception handling, and pagination. It's the kind of service you'd find behind a real e-commerce storefront, so the patterns transfer directly to professional work.

## Learning Objectives

By the end of this project you will be able to:

- Design a layered Spring Boot application (controller → service → repository).
- Model entities and relationships with JPA/Hibernate.
- Map between entities and DTOs to decouple your API contract from the database.
- Implement validation with `jakarta.validation` annotations.
- Build paginated, sortable, and filterable list endpoints with `Pageable`.
- Centralize error handling using `@RestControllerAdvice`.
- Test endpoints with `MockMvc`.

## Prerequisites & Setup

You need:

- **JDK 17+** (`java -version` should report 17 or higher)
- **Maven 3.8+**
- An HTTP client (curl, HTTPie, or Postman)

Generate the project with Spring Initializr from the command line:

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web,data-jpa,validation,h2 \
  -d type=maven-project \
  -d javaVersion=17 \
  -d bootVersion=3.3.0 \
  -d groupId=com.tlp \
  -d artifactId=product-catalog \
  -d name=product-catalog \
  -d packageName=com.tlp.catalog \
  -o product-catalog.zip

unzip product-catalog.zip -d product-catalog
cd product-catalog
./mvnw spring-boot:run
```

Configure an in-memory H2 database (`src/main/resources/application.yml`):

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:catalog;DB_CLOSE_DELAY=-1
    username: sa
    password: ""
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
  h2:
    console:
      enabled: true
```

## Requirements

| # | Capability | Endpoint |
|---|------------|----------|
| 1 | Create a product | `POST /api/products` |
| 2 | Get a product by id | `GET /api/products/{id}` |
| 3 | List products (paged, sortable, filter by category) | `GET /api/products` |
| 4 | Update a product | `PUT /api/products/{id}` |
| 5 | Delete a product | `DELETE /api/products/{id}` |
| 6 | Manage categories | `GET/POST /api/categories` |

A product has: `id`, `name`, `description`, `price`, `sku` (unique), `stock`, and a `category`. All write operations must validate input and return `400` with a structured error body on failure. Unknown ids return `404`.

## Step-by-Step Tasks

### 1. Model the domain

- [ ] Create a `Category` entity (`id`, `name`).
- [ ] Create a `Product` entity with a `@ManyToOne` link to `Category`.
- [ ] Add a unique constraint on `sku`.

```java
@Entity
@Table(name = "products")
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    private String description;

    @Column(nullable = false)
    private BigDecimal price;

    @Column(nullable = false, unique = true)
    private String sku;

    private int stock;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "category_id")
    private Category category;

    // getters & setters
}
```

### 2. Create repositories

- [ ] `ProductRepository extends JpaRepository<Product, Long>`.
- [ ] Add a query method to filter by category id with paging.

```java
public interface ProductRepository extends JpaRepository<Product, Long> {
    Page<Product> findByCategoryId(Long categoryId, Pageable pageable);
    boolean existsBySku(String sku);
}
```

### 3. Define request/response DTOs with validation

- [ ] Create a `ProductRequest` record with validation annotations.
- [ ] Create a `ProductResponse` record for output.

```java
public record ProductRequest(
        @NotBlank String name,
        String description,
        @NotNull @DecimalMin("0.0") BigDecimal price,
        @NotBlank String sku,
        @Min(0) int stock,
        @NotNull Long categoryId) {}

public record ProductResponse(
        Long id, String name, String description,
        BigDecimal price, String sku, int stock, String categoryName) {}
```

### 4. Build the service layer

- [ ] Map DTO → entity on create/update and entity → DTO on read.
- [ ] Throw a custom `ResourceNotFoundException` when an id is missing.
- [ ] Reject duplicate SKUs.

```java
@Service
public class ProductService {

    private final ProductRepository products;
    private final CategoryRepository categories;

    public ProductService(ProductRepository p, CategoryRepository c) {
        this.products = p;
        this.categories = c;
    }

    public ProductResponse create(ProductRequest req) {
        if (products.existsBySku(req.sku()))
            throw new DuplicateSkuException(req.sku());
        Category cat = categories.findById(req.categoryId())
                .orElseThrow(() -> new ResourceNotFoundException("Category", req.categoryId()));
        Product saved = products.save(toEntity(req, cat));
        return toResponse(saved);
    }
    // findById, list, update, delete ...
}
```

### 5. Expose the controller

- [ ] Wire up all six endpoints.
- [ ] Return `201 Created` with a `Location` header on create.
- [ ] Accept `Pageable` for the list endpoint.

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService service;

    public ProductController(ProductService service) { this.service = service; }

    @PostMapping
    public ResponseEntity<ProductResponse> create(@Valid @RequestBody ProductRequest req) {
        ProductResponse created = service.create(req);
        return ResponseEntity
                .created(URI.create("/api/products/" + created.id()))
                .body(created);
    }

    @GetMapping
    public Page<ProductResponse> list(
            @RequestParam(required = false) Long categoryId,
            Pageable pageable) {
        return service.list(categoryId, pageable);
    }

    @GetMapping("/{id}")
    public ProductResponse get(@PathVariable Long id) { return service.findById(id); }
}
```

### 6. Centralize error handling

- [ ] Add a `@RestControllerAdvice` that maps exceptions to consistent JSON.

```java
@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String, Object>> notFound(ResourceNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(Map.of("status", 404, "error", ex.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> invalid(MethodArgumentNotValidException ex) {
        Map<String, String> fields = new HashMap<>();
        ex.getBindingResult().getFieldErrors()
          .forEach(e -> fields.put(e.getField(), e.getDefaultMessage()));
        return ResponseEntity.badRequest()
                .body(Map.of("status", 400, "error", "Validation failed", "fields", fields));
    }
}
```

### 7. Verify it works

```bash
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Wireless Mouse","price":24.99,"sku":"MOU-001","stock":50,"categoryId":1}'

curl "http://localhost:8080/api/products?categoryId=1&page=0&size=10&sort=price,desc"
```

## Acceptance Criteria

- [ ] `POST /api/products` returns `201` and a `Location` header.
- [ ] Invalid payloads return `400` with a `fields` map naming each bad field.
- [ ] `GET /api/products/{id}` returns `404` for unknown ids.
- [ ] The list endpoint supports `page`, `size`, `sort`, and `categoryId`.
- [ ] Duplicate SKUs are rejected with a `409` (or `400`).
- [ ] Responses use `ProductResponse`, never the raw entity.
- [ ] At least one `MockMvc` test covers create + read.

## Stretch Challenges

1. Add **optimistic locking** with a `@Version` field to prevent lost updates.
2. Replace `ddl-auto` with **Flyway** migrations for versioned schema control.
3. Add **full-text search** on name/description using a `@Query` with `LIKE`.
4. Document the API with **springdoc-openapi** and serve Swagger UI.
5. Add **PATCH** support for partial updates (e.g. stock adjustments only).

## Hints

- Use `@Valid` on the `@RequestBody` parameter; validation is *not* triggered without it.
- For sorting, you don't parse query params yourself — Spring binds `?sort=price,desc` into `Pageable` automatically.
- Keep `BigDecimal` for `price` (never `double`) to avoid rounding errors with money.
- A `@ManyToOne` defaults to eager fetching; set `fetch = FetchType.LAZY` to avoid unnecessary joins.
- Map entities to DTOs in the service layer so a JPA change never silently alters your public contract.
