# Problem Details and Consistent Error Responses

Every production API eventually needs to answer the question: "what does a failed response look like?" Ad-hoc error bodies — each controller team inventing their own JSON shape — force clients to parse a dozen different formats. Spring Boot 3 ships with first-class support for **RFC 9457 Problem Details**, giving you a standard structure out of the box while leaving room for custom fields.

## The RFC 9457 Problem Details format

RFC 9457 (formerly RFC 7807) defines a JSON (and XML) media type `application/problem+json` with five standard members:

| Field | Type | Description |
|---|---|---|
| `type` | URI | A URI identifying the problem type (can be `about:blank`) |
| `title` | String | Short, human-readable summary of the problem |
| `status` | Integer | HTTP status code |
| `detail` | String | Human-readable explanation specific to this occurrence |
| `instance` | URI | A URI that identifies the specific occurrence |

A minimal problem response looks like this:

```json
{
  "type": "https://example.com/problems/product-not-found",
  "title": "Product Not Found",
  "status": 404,
  "detail": "No product with id 42 exists.",
  "instance": "/api/products/42"
}
```

## Enabling Problem Details in Spring Boot 3

Spring Boot 3 auto-configures `ProblemDetailsExceptionHandler` whenever you set one property:

```properties
# application.properties
spring.mvc.problemdetails.enabled=true
```

With this enabled, Spring automatically converts `ResponseStatusException`, `MethodArgumentNotValidException`, `HttpMessageNotReadableException`, and several other built-in exceptions into properly structured Problem Detail responses. No extra dependencies are needed — `spring-boot-starter-web` includes everything.

## Using ProblemDetail in your own handlers

The `ProblemDetail` class (in `org.springframework.http`) is the central building block. Use it inside a `@RestControllerAdvice` to produce consistent error responses across your entire API.

```java
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ProductNotFoundException.class)
    public ProblemDetail handleProductNotFound(ProductNotFoundException ex,
                                               HttpServletRequest request) {
        ProblemDetail problem = ProblemDetail
                .forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());

        problem.setTitle("Product Not Found");
        problem.setType(URI.create("https://api.example.com/problems/product-not-found"));
        problem.setInstance(URI.create(request.getRequestURI()));

        return problem;  // Spring sets Content-Type: application/problem+json automatically
    }
}
```

The `ProductNotFoundException` is a plain runtime exception:

```java
public class ProductNotFoundException extends RuntimeException {
    public ProductNotFoundException(Long id) {
        super("No product with id " + id + " exists.");
    }
}
```

## Adding custom extension fields

RFC 9457 explicitly allows extra fields beyond the five standard ones. Call `setProperty` to attach them:

```java
@ExceptionHandler(ValidationException.class)
public ProblemDetail handleValidation(ValidationException ex) {
    ProblemDetail problem = ProblemDetail
            .forStatusAndDetail(HttpStatus.UNPROCESSABLE_ENTITY, "Input validation failed.");

    problem.setTitle("Validation Error");
    problem.setProperty("errors", ex.getFieldErrors());   // custom extension
    problem.setProperty("timestamp", Instant.now());

    return problem;
}
```

The serialized response will include `errors` and `timestamp` alongside the standard fields, which clients can use for richer error display.

## Handling Bean Validation errors

When you use `@Valid` on a request body, Spring throws `MethodArgumentNotValidException` on failure. With `spring.mvc.problemdetails.enabled=true` this is already handled automatically. To customize it, override in your advice:

```java
@ExceptionHandler(MethodArgumentNotValidException.class)
public ProblemDetail handleBeanValidation(MethodArgumentNotValidException ex) {
    ProblemDetail problem = ProblemDetail
            .forStatusAndDetail(HttpStatus.BAD_REQUEST, "Request body contains invalid fields.");

    problem.setTitle("Validation Failed");

    List<String> errors = ex.getBindingResult().getFieldErrors().stream()
            .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
            .toList();

    problem.setProperty("errors", errors);
    return problem;
}
```

Sample response:

```json
{
  "type": "about:blank",
  "title": "Validation Failed",
  "status": 400,
  "detail": "Request body contains invalid fields.",
  "instance": "/api/products",
  "errors": ["name: must not be blank", "price: must be greater than 0"]
}
```

## Common mistakes and best practices

- **Do not return `200 OK` with an error body.** Always set the correct HTTP status; clients and monitoring tools rely on it.
- **Keep `detail` user-safe.** Never expose stack traces or internal class names — put diagnostic information in logs, not in the response.
- **Use `about:blank` for `type` when you have no documentation URI yet.** It is valid per the RFC and avoids broken links.
- **Centralize all exception mapping in one `@RestControllerAdvice`.** Scattering `try/catch` blocks in controllers duplicates logic and makes the response format inconsistent.
- **Set `Content-Type: application/problem+json` correctly.** Spring does this automatically when you return `ProblemDetail`; do not return `ResponseEntity<Map<String, Object>>` to simulate it manually.

## Summary

Spring Boot 3's built-in `ProblemDetail` class and `spring.mvc.problemdetails.enabled=true` property give you RFC 9457-compliant error responses with minimal code; pair them with a single `@RestControllerAdvice` to enforce a consistent error contract across your entire API.
