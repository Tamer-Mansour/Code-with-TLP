# Pagination and Sorting

Returning an entire database table in a single HTTP response is a scalability anti-pattern. Spring Data's `Pageable` abstraction lets you slice any repository query into pages and sort the results — all with virtually no boilerplate.

---

## The `Pageable` Interface

`org.springframework.data.domain.Pageable` encapsulates three things:

| Field | Description | Default (if using `@PageableDefault`) |
|-------|-------------|--------------------------------------|
| `page` | Zero-based page index | `0` |
| `size` | Number of records per page | `20` |
| `sort` | One or more `property,direction` pairs | unsorted |

Spring Data JPA translates a `Pageable` directly into a SQL `LIMIT` / `OFFSET` + `ORDER BY` clause, so you never write that SQL by hand.

---

## Step 1 — Add Spring Data JPA

If it is not already in your `pom.xml`:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
```

---

## Step 2 — Extend `JpaRepository`

`JpaRepository` extends `PagingAndSortingRepository`, which already declares `findAll(Pageable pageable)`. No extra code is needed in your repository interface.

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    // Custom query that also supports pagination
    Page<Product> findByCategoryIgnoreCase(String category, Pageable pageable);
}
```

The return type `Page<T>` wraps the slice of results **and** carries metadata (total elements, total pages, current page number, etc.).

---

## Step 3 — Accept `Pageable` in the Controller

Spring MVC resolves `Pageable` automatically from query parameters when `spring-data-web` support is on the classpath (it is, with `spring-boot-starter-data-jpa`).

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductRepository repository;

    public ProductController(ProductRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public Page<Product> list(
            @RequestParam(defaultValue = "") String category,
            @PageableDefault(size = 10, sort = "name") Pageable pageable) {

        if (category.isBlank()) {
            return repository.findAll(pageable);
        }
        return repository.findByCategoryIgnoreCase(category, pageable);
    }
}
```

`@PageableDefault` sets the fallback values that apply when the client omits `page`, `size`, or `sort`.

---

## Calling the Endpoint

```
# Page 0, 5 items per page, sorted by price ascending
GET /api/products?page=0&size=5&sort=price,asc

# Sort by multiple fields: name asc, then price desc
GET /api/products?sort=name,asc&sort=price,desc

# Filter + paginate
GET /api/products?category=electronics&page=1&size=10&sort=name,asc
```

---

## The `Page<T>` Response Shape

Spring serializes `Page<T>` to JSON automatically:

```json
{
  "content": [
    { "id": 1, "name": "Keyboard", "price": 49.99 },
    { "id": 2, "name": "Monitor",  "price": 199.99 }
  ],
  "pageable": {
    "pageNumber": 0,
    "pageSize": 2,
    "sort": { "sorted": true, "unsorted": false }
  },
  "totalElements": 84,
  "totalPages": 42,
  "last": false,
  "first": true,
  "numberOfElements": 2
}
```

The `totalElements` and `totalPages` fields come from a `COUNT(*)` query Spring Data runs automatically — no extra repository method required.

---

## Using `Slice` When You Don't Need a Total Count

For very large tables, the `COUNT(*)` query can be expensive. Use `Slice<T>` instead of `Page<T>` to skip it; the trade-off is that you lose `totalPages` and `totalElements`.

```java
Slice<Product> findTop50ByOrderByCreatedAtDesc(Pageable pageable);
```

`Slice` tells you only whether there is a **next** page (`hasNext()`), which is all an infinite-scroll UI needs.

---

## Common Mistakes and Best Practices

- **Never return `List<T>` from a paginated endpoint.** Without `Page` or `Slice`, the client has no way to know whether more data exists.
- **Validate `size` to prevent abuse.** A client requesting `size=100000` will cause an out-of-memory problem. Cap it with `@Max` on the `size` parameter or configure `spring.data.web.pageable.max-page-size` in `application.properties`.
- **Only sort on indexed columns.** Sorting on a non-indexed column causes a full table scan. Add a database index for every field you allow clients to sort by.
- **Expose a DTO, not the JPA entity, in `Page<T>`.** Use `repository.findAll(pageable).map(ProductDTO::from)` to project before serialization.
- **Zero-based page index can confuse clients.** Document it clearly, or use `@PageableDefault` and `one-indexed-parameters: true` in `application.properties` to switch to 1-based indexing.

```properties
# application.properties — switch to 1-based page numbers
spring.data.web.pageable.one-indexed-parameters=true
```

---

## Summary

Spring Data's `Pageable` + `Page<T>` combination gives you database-level pagination and multi-column sorting through query parameters alone, keeping your controller code minimal and your API responses self-describing with total-count metadata.
