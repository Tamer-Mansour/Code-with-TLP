# Bean Validation with Jakarta Validation

Accepting whatever a client sends is a security and reliability risk. Jakarta Bean Validation (formerly Javax Validation) is the standard specification for expressing constraints directly on your Java model classes. Spring Boot 3 ships with Hibernate Validator, the reference implementation, so you get full validation support with a single dependency.

---

## Adding the Dependency

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

This pulls in `hibernate-validator` and the `jakarta.validation-api` transitively — no version needed when using the Spring Boot parent BOM.

---

## Annotating a DTO

Place constraint annotations on the fields (or constructor parameters for records) of your request DTO.

```java
import jakarta.validation.constraints.*;

public record CreateProductRequest(

        @NotBlank(message = "Name is required")
        @Size(min = 2, max = 100, message = "Name must be between 2 and 100 characters")
        String name,

        @Size(max = 500, message = "Description cannot exceed 500 characters")
        String description,

        @NotNull(message = "Price is required")
        @DecimalMin(value = "0.01", message = "Price must be greater than 0")
        BigDecimal price,

        @Min(value = 0, message = "Stock cannot be negative")
        int stock
) {}
```

---

## Triggering Validation in the Controller

Add `@Valid` (or `@Validated`) to the parameter annotated with `@RequestBody`. If any constraint fails, Spring throws a `MethodArgumentNotValidException` before your method body executes.

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ProductResponse create(@Valid @RequestBody CreateProductRequest request) {
        return productService.create(request);
    }
}
```

Without `@Valid` the annotations on the DTO are silently ignored — this is the single most common mistake.

---

## Common Constraint Annotations

| Annotation | Applies To | What It Checks |
|---|---|---|
| `@NotNull` | Any object | Field reference is not null |
| `@NotBlank` | String | Not null and contains non-whitespace |
| `@NotEmpty` | String, Collection | Not null and not empty |
| `@Size(min, max)` | String, Collection | Length or size within range |
| `@Min(value)` / `@Max(value)` | Integer types | Numeric value boundary |
| `@DecimalMin` / `@DecimalMax` | BigDecimal, String | Decimal value boundary |
| `@Email` | String | Matches email format |
| `@Pattern(regexp)` | String | Matches a regular expression |
| `@Positive` / `@PositiveOrZero` | Numeric types | Value > 0 or >= 0 |
| `@Past` / `@Future` | Date/Time types | Date is before/after now |

---

## Returning Structured Validation Errors

By default, a `MethodArgumentNotValidException` returns a verbose 400 response. Define a `@RestControllerAdvice` to produce clean JSON instead.

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Map<String, Object> handleValidationErrors(MethodArgumentNotValidException ex) {
        Map<String, String> fieldErrors = new LinkedHashMap<>();

        ex.getBindingResult().getFieldErrors().forEach(error ->
                fieldErrors.put(error.getField(), error.getDefaultMessage())
        );

        return Map.of(
                "status", 400,
                "error", "Validation Failed",
                "errors", fieldErrors
        );
    }
}
```

A client sending an empty `name` and a negative `price` now receives:

```json
{
  "status": 400,
  "error": "Validation Failed",
  "errors": {
    "name": "Name is required",
    "price": "Price must be greater than 0"
  }
}
```

---

## Validating Path Variables and Query Parameters

To validate `@PathVariable` and `@RequestParam` values, add `@Validated` at the **class level** of the controller (not just the method parameter).

```java
@RestController
@RequestMapping("/api/products")
@Validated
public class ProductController {

    @GetMapping("/{id}")
    public ProductResponse getById(
            @PathVariable @Positive(message = "ID must be positive") Long id) {
        return productService.findById(id);
    }
}
```

Constraint violations on path/query params throw `ConstraintViolationException`. Handle it in the same `@RestControllerAdvice`:

```java
@ExceptionHandler(ConstraintViolationException.class)
@ResponseStatus(HttpStatus.BAD_REQUEST)
public Map<String, Object> handleConstraintViolation(ConstraintViolationException ex) {
    Map<String, String> errors = new LinkedHashMap<>();
    ex.getConstraintViolations().forEach(v ->
            errors.put(v.getPropertyPath().toString(), v.getMessage())
    );
    return Map.of("status", 400, "error", "Validation Failed", "errors", errors);
}
```

---

## Common Mistakes and Best Practices

- **Forgetting `@Valid`.** The annotations on the DTO do nothing without it on the controller parameter.
- **Using `@NotNull` on a primitive.** Primitives (`int`, `long`) can never be null; use `@Min`/`@Max` directly, or switch to boxed types (`Integer`, `Long`) if null-check is also needed.
- **Mixing `@Valid` and `@Validated` incorrectly.** Use `@Valid` for `@RequestBody` cascade validation; use `@Validated` on the class to enable method-level constraint processing for path/query params.
- **Relying on default messages in production.** Always provide a `message` attribute — default messages leak implementation details and are not localisation-friendly.
- **Validating inside the service instead of the controller.** Catching bad input at the HTTP boundary is cheaper and keeps service code focused on business logic.

---

## Summary

Annotate your DTOs with `jakarta.validation.constraints.*`, mark the controller parameter with `@Valid`, and handle `MethodArgumentNotValidException` in a `@RestControllerAdvice` — this three-step pattern gives you declarative, consistent input validation across every endpoint with minimal boilerplate.
