# Path Variables, Query Params, and Request Bodies

Every HTTP request carries data in one of three places: embedded in the URL path, appended as query parameters, or sent in the request body. Spring MVC gives you a dedicated annotation for each case, and choosing the right one is a foundational REST design decision.

---

## Path Variables — `@PathVariable`

A path variable is a dynamic segment of the URL itself. Use it to identify a specific resource.

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    @GetMapping("/{id}")
    public Product getById(@PathVariable Long id) {
        return productService.findById(id);
    }

    // Multiple path variables in one route
    @GetMapping("/{categoryId}/items/{itemId}")
    public Item getItem(
            @PathVariable Long categoryId,
            @PathVariable Long itemId) {
        return itemService.findItem(categoryId, itemId);
    }
}
```

By default the variable name in `{}` must match the parameter name. If they differ, use the `name` attribute:

```java
@GetMapping("/{prod_id}")
public Product get(@PathVariable(name = "prod_id") Long id) { ... }
```

---

## Query Parameters — `@RequestParam`

Query parameters (`?key=value`) are best for optional filters, pagination, search, and sorting — anything that refines a collection rather than identifying a single resource.

```java
@GetMapping
public List<Product> search(
        @RequestParam(defaultValue = "") String name,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size) {
    return productService.search(name, page, size);
}
```

Example request:

```
GET /api/products?name=laptop&page=0&size=10
```

Key attributes of `@RequestParam`:

| Attribute | Purpose | Default |
|-----------|---------|---------|
| `value` / `name` | Query string key to bind | parameter name |
| `required` | Throw 400 if missing | `true` |
| `defaultValue` | Value when the param is absent | (none) |

Setting `defaultValue` implicitly makes the param optional (`required` becomes `false`).

---

## Request Body — `@RequestBody`

The request body carries structured data, almost always JSON. Spring Boot auto-configures Jackson, so annotating the parameter with `@RequestBody` deserializes the JSON into your Java object automatically.

```java
// DTO — plain record (Java 16+)
public record CreateProductRequest(
        String name,
        String description,
        double price,
        int stock) {}

@PostMapping
@ResponseStatus(HttpStatus.CREATED)
public Product create(@RequestBody CreateProductRequest request) {
    return productService.create(request);
}

@PutMapping("/{id}")
public Product update(
        @PathVariable Long id,
        @RequestBody CreateProductRequest request) {
    return productService.update(id, request);
}
```

A matching request body:

```json
{
  "name": "Wireless Mouse",
  "description": "Ergonomic 2.4 GHz mouse",
  "price": 29.99,
  "stock": 150
}
```

---

## Choosing the Right Approach

| Data | Annotation | Typical HTTP Methods |
|------|-----------|----------------------|
| Resource identifier in the URL | `@PathVariable` | GET, PUT, PATCH, DELETE |
| Optional filters / pagination | `@RequestParam` | GET |
| Structured payload | `@RequestBody` | POST, PUT, PATCH |

You can freely combine all three in a single handler:

```java
@PatchMapping("/{id}/inventory")
public Product adjustStock(
        @PathVariable Long id,
        @RequestParam(defaultValue = "false") boolean notify,
        @RequestBody StockAdjustmentRequest body) {
    return productService.adjustStock(id, body.delta(), notify);
}
```

---

## Common Mistakes and Best Practices

- **Do not use `@RequestBody` on GET requests.** Although technically possible with some clients, it violates the HTTP spec and will break standard tooling.
- **Validate early.** Pair `@RequestBody` with `@Valid` and Jakarta Validation annotations (`@NotBlank`, `@Min`, etc.) to reject bad input before it reaches your service layer. Validation is covered in a dedicated lesson.
- **Use DTOs, not entities, as request bodies.** Exposing a JPA entity directly can lead to mass-assignment vulnerabilities and tight coupling.
- **Keep path variables mandatory.** If you need an optional identifier, use a query param instead.
- **Prefer `defaultValue` over `required = false`.** A missing `required = false` param returns `null`, which requires null-checks throughout your code; a `defaultValue` gives you a safe fallback immediately.
- **Name paths after resources, not actions.** `/products/{id}` is correct; `/getProduct?id=1` conflates REST and RPC style.

---

## Summary

`@PathVariable` identifies a resource, `@RequestParam` refines a query, and `@RequestBody` carries a structured payload — each maps directly to a distinct part of an HTTP request. Choosing the correct annotation for each piece of incoming data is the single most important habit for writing clean, idiomatic Spring REST controllers.
