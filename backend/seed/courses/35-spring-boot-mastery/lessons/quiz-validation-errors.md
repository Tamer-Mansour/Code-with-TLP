# Quiz: Validation & Error Handling

Test your understanding of Bean Validation (Jakarta Validation 3), Spring Boot's integration with
`@Valid` / `@Validated`, constraint annotations, `BindingResult`, global exception handling with
`@ControllerAdvice`, `ProblemDetail` (RFC 7807), and custom validators.

---

**Q1. Which annotation must be placed on a controller method parameter to trigger Jakarta Bean Validation on the incoming request body?**
- [ ] `@Validate`
- [ ] `@Constraint`
- [ ] `@NotNull`
- [x] `@Valid`

---

**Q2. A developer writes the following controller method. What HTTP status code does Spring Boot return by default when validation of the request body fails?**

```java
@PostMapping("/users")
public ResponseEntity<UserDto> create(@Valid @RequestBody UserDto dto) {
    return ResponseEntity.ok(userService.save(dto));
}
```

- [ ] 500 Internal Server Error
- [x] 400 Bad Request
- [ ] 422 Unprocessable Entity
- [ ] 409 Conflict

---

**Q3. Which of the following sets of annotations correctly constrains a `User` DTO so that `email` is a well-formed address and `age` must be at least 18?**

```java
// Option A
public class UserDto {
    @Email
    private String email;

    @Min(18)
    private int age;
}

// Option B
public class UserDto {
    @NotNull
    private String email;

    @Positive
    private int age;
}

// Option C
public class UserDto {
    @Pattern(regexp = ".*")
    private String email;

    @Max(18)
    private int age;
}

// Option D
public class UserDto {
    @Size(min = 5)
    private String email;

    @Min(0)
    private int age;
}
```

- [x] Option A
- [ ] Option B
- [ ] Option C
- [ ] Option D

---

**Q4. What is the purpose of `@ControllerAdvice` in Spring Boot error handling?**
- [ ] It validates method parameters inside service-layer beans.
- [ ] It replaces the embedded Tomcat error page with a custom HTML template.
- [x] It defines centralized exception-handler methods (annotated with `@ExceptionHandler`) that apply across multiple controllers.
- [ ] It enables AOP-based transaction management on controller methods.

---

**Q5. Examine the following exception handler. Which statement about its behavior is correct?**

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> handleValidation(
            MethodArgumentNotValidException ex) {

        Map<String, String> errors = new LinkedHashMap<>();
        ex.getBindingResult().getFieldErrors()
          .forEach(fe -> errors.put(fe.getField(), fe.getDefaultMessage()));

        return ResponseEntity.badRequest().body(errors);
    }
}
```

- [ ] It catches all `RuntimeException` subtypes and returns a 500 response.
- [ ] `@RestControllerAdvice` is not a valid Spring annotation; `@ControllerAdvice` must be used instead.
- [ ] The handler will silently swallow validation errors and return an empty 200 response.
- [x] It catches `MethodArgumentNotValidException`, collects field-level error messages into a map, and returns a 400 response with that map as the JSON body.

---

**Q6. Which table correctly maps Jakarta Validation constraint annotations to their intended purpose?**

| Annotation | Validates |
|---|---|
| `@NotBlank` | String is not null, not empty, and not whitespace-only |
| `@Size(min=2, max=50)` | String length or collection size is within bounds |
| `@Pattern(regexp="…")` | String matches the given regular expression |
| `@Positive` | Number is strictly greater than zero |

A developer uses `@NotEmpty` on a `String` field. What does `@NotEmpty` guarantee that `@NotNull` does **not**?

- [ ] The string is a valid email address.
- [ ] The string contains no whitespace characters.
- [x] The string is not null **and** has at least one character (length > 0).
- [ ] The string length does not exceed 255 characters.

---

**Q7. A service method is annotated as shown below. What must be true for the `@Min` constraint on the parameter to be enforced at runtime?**

```java
@Service
@Validated
public class OrderService {

    public Order placeOrder(@Min(1) int quantity) {
        // ...
    }
}
```

- [ ] The `@Min` annotation is only valid on DTO fields; it has no effect on method parameters.
- [ ] `@Valid` must be added to the method itself, not to the class.
- [ ] Spring Boot enforces method-level constraints automatically without any extra annotation on the class.
- [x] The class must be annotated with `@Validated` so Spring creates a proxy that intercepts calls and runs Bean Validation on the method parameters.

---

**Q8. Spring Boot 3 introduced first-class support for RFC 7807 "Problem Details for HTTP APIs" via `ProblemDetail`. Which property must be set in `application.properties` to make Spring's built-in exception handlers (such as `ResponseEntityExceptionHandler`) return `ProblemDetail` JSON bodies automatically?**

```properties
# Which entry enables RFC 7807 problem details?
```

- [ ] `spring.mvc.error.include-message=always`
- [ ] `spring.web.problem-details.format=rfc7807`
- [x] `spring.mvc.problemdetails.enabled=true`
- [ ] `server.error.whitelabel.enabled=false`

---

**Q9. A developer creates a custom constraint annotation `@ValidUsername`. Which two elements are required to make it functional?**

```java
@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = UsernameValidator.class)
public @interface ValidUsername {
    String message() default "Invalid username";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

- [ ] A `@Component`-annotated service and a `@Repository` for persistence checks.
- [ ] An `@ExceptionHandler` method and a `@ControllerAdvice` class.
- [x] The `@Constraint(validatedBy = …)` meta-annotation pointing to a `ConstraintValidator<ValidUsername, String>` implementation, plus the three mandatory attributes (`message`, `groups`, `payload`).
- [ ] A `Validator` bean registered in `application.properties` and a `FilterChain` entry.

---

**Q10. Given the following `@ExceptionHandler` method inside a `@RestControllerAdvice`, what is returned when a `ResourceNotFoundException` is thrown from any controller?**

```java
@ExceptionHandler(ResourceNotFoundException.class)
public ProblemDetail handleNotFound(ResourceNotFoundException ex,
                                    HttpServletRequest request) {
    ProblemDetail pd = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND, ex.getMessage());
    pd.setTitle("Resource Not Found");
    pd.setInstance(URI.create(request.getRequestURI()));
    return pd;
}
```

- [ ] A plain-text string containing the exception message with HTTP 500.
- [ ] An empty HTTP 404 response with no body.
- [ ] A redirect to the `/error` endpoint managed by `BasicErrorController`.
- [x] A JSON body conforming to RFC 7807 with `status: 404`, the exception message as `detail`, `"Resource Not Found"` as `title`, and the request URI as `instance`, all with HTTP 404.
