# Global Exception Handling with @ControllerAdvice

When an exception escapes a controller in Spring Boot, the default behaviour is to return a generic error response. For a real API you want **consistent, structured error payloads** with the right HTTP status — not stack traces leaking to clients. Spring's `@ControllerAdvice` lets you centralize exception handling in one place instead of scattering `try/catch` across every controller.

## What @ControllerAdvice does

`@ControllerAdvice` is a specialization of `@Component` that applies cross-cutting concerns to all `@RequestMapping` methods. Combined with `@ExceptionHandler` methods, it intercepts exceptions thrown anywhere in your controllers and maps them to HTTP responses.

The companion annotation `@RestControllerAdvice` is simply `@ControllerAdvice` + `@ResponseBody`, so handler return values are serialized straight to the response body (JSON) — which is what you want for REST APIs.

## A consistent error response

First, define a small DTO so every error looks the same:

```java
public record ApiError(
        Instant timestamp,
        int status,
        String error,
        String message,
        String path) {
}
```

## The global handler

```java
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import jakarta.servlet.http.HttpServletRequest;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ApiError> handleNotFound(
            ResourceNotFoundException ex, HttpServletRequest request) {

        ApiError body = new ApiError(
                Instant.now(),
                HttpStatus.NOT_FOUND.value(),
                "Not Found",
                ex.getMessage(),
                request.getRequestURI());

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(body);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> handleValidation(
            MethodArgumentNotValidException ex) {

        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(fieldError ->
                errors.put(fieldError.getField(), fieldError.getDefaultMessage()));

        return ResponseEntity.badRequest().body(errors);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiError> handleGeneric(
            Exception ex, HttpServletRequest request) {

        ApiError body = new ApiError(
                Instant.now(),
                HttpStatus.INTERNAL_SERVER_ERROR.value(),
                "Internal Server Error",
                "Something went wrong",
                request.getRequestURI());

        return ResponseEntity.internalServerError().body(body);
    }
}
```

`MethodArgumentNotValidException` is thrown automatically when a `@Valid` request body fails Bean Validation, so this handler turns field constraint violations into a clean `400` map.

## Mapping status with @ResponseStatus

For simple cases you can annotate the exception itself, avoiding an explicit handler:

```java
@ResponseStatus(HttpStatus.NOT_FOUND)
public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String message) {
        super(message);
    }
}
```

## Choosing an approach

| Approach | Scope | Custom body? | Best for |
|----------|-------|--------------|----------|
| `@ResponseStatus` on exception | That exception type | No | Quick status mapping |
| `@ExceptionHandler` in a controller | One controller | Yes | Controller-specific logic |
| `@RestControllerAdvice` | All controllers | Yes | App-wide, consistent errors |
| Extend `ResponseEntityExceptionHandler` | All controllers | Yes | Override Spring's built-in MVC exceptions |

## Common mistakes and best practices

- **Don't leak internals.** Never put `ex.getMessage()` of an arbitrary `Exception` into the response for `500`s — log it server-side instead.
- **Order matters by specificity, not declaration.** Spring picks the handler for the most specific exception type, so a broad `Exception.class` handler won't shadow narrower ones.
- **Log before returning.** Add `log.error("Unhandled error", ex)` in the generic handler so you keep the stack trace.
- **Reuse, don't duplicate.** Keep a single `@RestControllerAdvice`; use `basePackages` on the annotation only if you need to scope it.
- **Prefer a typed DTO** (or RFC 7807 `ProblemDetail`, built into Spring Boot 3) over ad-hoc maps for production APIs.

## Summary

`@RestControllerAdvice` with `@ExceptionHandler` methods centralizes error handling, producing consistent, well-structured responses with correct HTTP status codes — while keeping sensitive details out of client payloads.
