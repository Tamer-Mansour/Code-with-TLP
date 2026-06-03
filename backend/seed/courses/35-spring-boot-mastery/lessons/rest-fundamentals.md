# REST Fundamentals

REST (Representational State Transfer) is the architectural style that underpins the modern web API ecosystem. Understanding its constraints is essential before writing a single line of Spring Boot controller code.

## The Six REST Constraints

REST is not a protocol or a standard — it is a set of architectural constraints defined by Roy Fielding in his 2000 dissertation. A service that satisfies these constraints is called **RESTful**.

| Constraint | What it means in practice |
|---|---|
| Uniform Interface | Resources are identified by URIs; representations are self-descriptive |
| Stateless | Each request contains all context needed; no session state on the server |
| Client-Server | UI concerns and data-storage concerns are separated |
| Cacheable | Responses declare whether they may be cached |
| Layered System | A client cannot tell whether it is connected directly to the origin server |
| Code on Demand (optional) | Servers may send executable code (e.g., JavaScript) to clients |

The **stateless** constraint has the biggest day-to-day impact: every HTTP request from a client must carry all information required to understand and complete it (authentication token, pagination cursor, etc.).

## Resources and URIs

A REST API models *resources*, not actions. A resource is a noun — a product, an order, a user.

Good URI design:

```
GET    /products          # list all products
GET    /products/{id}     # fetch one product
POST   /products          # create a product
PUT    /products/{id}     # replace a product
PATCH  /products/{id}     # partial update
DELETE /products/{id}     # remove a product
```

Avoid verb-based paths (`/getProduct`, `/createProduct`). Let the HTTP method carry the verb.

## HTTP Methods and Their Semantics

```
GET    — safe, idempotent  — read only, no side effects
POST   — neither           — creates a resource; not idempotent
PUT    — idempotent        — full replacement; repeated calls yield same result
PATCH  — not idempotent*   — partial update
DELETE — idempotent        — repeated deletes are safe (resource already gone)
```

**Idempotent** means calling the operation N times produces the same server state as calling it once. This property matters for retry logic in distributed systems.

## HTTP Status Codes You Must Know

| Code | Meaning | Typical REST usage |
|---|---|---|
| 200 OK | Success | GET, PUT, PATCH responses |
| 201 Created | Resource created | POST response; include `Location` header |
| 204 No Content | Success, no body | DELETE response |
| 400 Bad Request | Invalid input | validation failure |
| 401 Unauthorized | Not authenticated | missing/invalid token |
| 403 Forbidden | Authenticated but not allowed | insufficient role |
| 404 Not Found | Resource absent | unknown ID |
| 409 Conflict | State conflict | duplicate email |
| 422 Unprocessable Entity | Semantic validation failure | business rule violation |
| 500 Internal Server Error | Server fault | unhandled exception |

## Representations and Content Negotiation

A resource has an identity (URI) and one or more *representations* (JSON, XML, CSV). The client advertises what it can accept via the `Accept` header; the server declares what it is returning via `Content-Type`.

```
Accept: application/json
Content-Type: application/json; charset=UTF-8
```

Spring Boot's `@RestController` serialises return values to JSON automatically via Jackson. You opt into content negotiation by listing `produces` on the mapping:

```java
@GetMapping(value = "/products/{id}", produces = MediaType.APPLICATION_JSON_VALUE)
public ResponseEntity<ProductDto> getProduct(@PathVariable Long id) {
    return ResponseEntity.ok(productService.findById(id));
}
```

## A Minimal Spring Boot REST Example

```java
@RestController
@RequestMapping("/api/v1/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping
    public List<ProductDto> list() {
        return productService.findAll();
    }

    @PostMapping
    public ResponseEntity<ProductDto> create(@Valid @RequestBody CreateProductRequest request) {
        ProductDto created = productService.create(request);
        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(created.id())
                .toUri();
        return ResponseEntity.created(location).body(created);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        productService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

Key points in this snippet:
- `@RestController` is shorthand for `@Controller` + `@ResponseBody`.
- Constructor injection is preferred over field injection (`@Autowired`).
- `POST` returns `201 Created` with a `Location` header pointing to the new resource.
- `DELETE` returns `204 No Content` — no body is needed.

## Common Mistakes

- **Returning 200 for a created resource** — use 201 and set the `Location` header.
- **Exposing entity classes directly** — always map to DTOs to avoid over-posting and leaking internal structure.
- **Embedding actions in URIs** — `/orders/{id}/cancel` is acceptable when there is no clean HTTP method mapping, but keep it rare.
- **Ignoring idempotency** — design `PUT` endpoints so retrying them is safe.

## Summary

REST is an architectural style built around stateless communication, uniform resource identification, and standard HTTP semantics. Internalising the correct mapping between HTTP methods, status codes, and resource URIs is the foundation every Spring Boot API is built on.
