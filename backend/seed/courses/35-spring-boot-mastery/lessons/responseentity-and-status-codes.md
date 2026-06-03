# ResponseEntity and HTTP Status Codes

REST APIs communicate intent through HTTP status codes. Returning a bare object from a controller works for happy paths, but real-world APIs need to carry status codes, custom headers, and sometimes an empty body. Spring's `ResponseEntity<T>` gives you full control over all three.

## What is ResponseEntity?

`ResponseEntity<T>` is a generic class that wraps three things:

- **Status code** — the HTTP response status (200, 201, 404, etc.)
- **Headers** — any HTTP response headers you want to add
- **Body** — the payload (can be `null`)

You return it from a `@RestController` method just like any other type, and Spring's `HttpMessageConverter` handles serialization of the body.

## Basic usage

The simplest form uses the static builder factory:

```java
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    // 200 OK with a body
    @GetMapping("/{id}")
    public ResponseEntity<Product> getById(@PathVariable Long id) {
        return productService.findById(id)
                .map(ResponseEntity::ok)                        // 200 OK
                .orElse(ResponseEntity.notFound().build());     // 404 Not Found, no body
    }

    // 201 Created with a Location header
    @PostMapping
    public ResponseEntity<Product> create(@RequestBody Product product) {
        Product saved = productService.save(product);
        URI location = URI.create("/api/products/" + saved.getId());
        return ResponseEntity.created(location).body(saved);   // 201 Created
    }

    // 204 No Content on delete
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        productService.delete(id);
        return ResponseEntity.noContent().build();              // 204 No Content
    }
}
```

Notice the three builder entry points: `ResponseEntity.ok(body)`, `ResponseEntity.created(uri)`, and `ResponseEntity.noContent()`. Each pre-sets the correct status code.

## Builder API cheatsheet

| Factory method | Status | Typical use |
|---|---|---|
| `ResponseEntity.ok(body)` | 200 OK | Successful GET, PUT |
| `ResponseEntity.created(uri)` | 201 Created | Successful POST that creates a resource |
| `ResponseEntity.accepted()` | 202 Accepted | Async/deferred processing |
| `ResponseEntity.noContent()` | 204 No Content | DELETE, or PUT with no return body |
| `ResponseEntity.badRequest()` | 400 Bad Request | Validation failure |
| `ResponseEntity.notFound()` | 404 Not Found | Resource does not exist |
| `ResponseEntity.status(code)` | any | Custom or less-common codes |

All of these return a `BodyBuilder` (or `HeadersBuilder`) that you finalize with `.body(T)` or `.build()`.

## Adding custom headers

```java
@GetMapping("/export")
public ResponseEntity<byte[]> exportCsv() {
    byte[] csv = reportService.generateCsv();

    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.TEXT_PLAIN);
    headers.setContentDispositionFormData("attachment", "report.csv");

    return ResponseEntity
            .ok()
            .headers(headers)
            .body(csv);
}
```

## Using HttpStatus enum directly

When the static helpers do not cover your case, pass an `HttpStatus` value explicitly:

```java
return ResponseEntity
        .status(HttpStatus.UNPROCESSABLE_ENTITY)
        .body(new ErrorResponse("Validation failed", errors));
```

`HttpStatus` covers all standard IANA-registered codes and is more readable than raw integers.

## Common mistakes and best practices

- **Do not always return 200.** Return 201 for resource creation, 204 when there is nothing to send back, and 404 when the resource is absent. Clients rely on these distinctions.
- **Build with `.build()`, not `.body(null)`.** For no-body responses, `.build()` is the idiomatic call; passing `null` to `.body()` compiles but signals a missing body rather than an intentional empty response.
- **Pair 201 with a `Location` header.** RFC 9110 requires it. Use `ResponseEntity.created(uri)` which sets both automatically.
- **Use `ResponseEntity<Void>` for empty bodies.** Declaring the generic as `Void` makes intent explicit; avoid `ResponseEntity<?>` unless the body type is genuinely unknown.
- **Centralize error responses with `@ControllerAdvice`.** Rather than repeating `ResponseEntity.status(HttpStatus.NOT_FOUND).body(...)` everywhere, handle exceptions in one place with `@ExceptionHandler`.

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ProductNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(ProductNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(new ErrorResponse(ex.getMessage()));
    }
}
```

## Summary

`ResponseEntity<T>` is the precise tool for crafting HTTP responses in Spring Boot: pair the right status code with your body and headers, use the static builder helpers for the most common codes, and push cross-cutting error mapping into a `@ControllerAdvice` class to keep controllers clean.
