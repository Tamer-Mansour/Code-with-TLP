# Spring Coding Challenges

Coding challenges are the fastest way to turn Spring Boot theory into muscle memory. This lesson walks through small, self-contained problems that exercise the core skills you'll use every day: dependency injection, REST endpoints, validation, persistence, and testing. Each challenge is solvable in a single class or two, with Java 17+ and Spring Boot 3.

## Why challenges work

Reading about `@Service` and `@Transactional` is not the same as wiring them yourself. Short challenges force you to make real decisions about layering, error handling, and bean configuration — the same decisions that show up in production code and technical interviews.

## Challenge 1: A validated REST endpoint

Build a `POST /api/users` endpoint that rejects bad input with a `400` and returns `201` on success. This combines Bean Validation (`jakarta.validation`) with a controller.

```java
public record CreateUserRequest(
        @NotBlank String name,
        @Email String email) {}

@RestController
@RequestMapping("/api/users")
class UserController {

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public CreateUserRequest create(@Valid @RequestBody CreateUserRequest req) {
        return req; // echo back; real code would persist
    }
}
```

The `@Valid` annotation triggers validation; a failing field throws `MethodArgumentNotValidException`. Add a handler so clients get a clean message instead of a stack trace:

```java
@RestControllerAdvice
class ApiExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Map<String, String> handle(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors()
          .forEach(e -> errors.put(e.getField(), e.getDefaultMessage()));
        return errors;
    }
}
```

## Challenge 2: Persist and query with Spring Data JPA

Given an `Order` entity, find all orders above a threshold. Spring Data derives the query from the method name — no SQL required.

```java
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByTotalGreaterThan(BigDecimal threshold);
}
```

If you need custom SQL, declare it explicitly:

```sql
SELECT * FROM orders WHERE total > :threshold AND status = 'PAID';
```

```java
@Query(value = "SELECT * FROM orders WHERE total > :t AND status = 'PAID'",
       nativeQuery = true)
List<Order> findPaidAbove(@Param("t") BigDecimal t);
```

## Difficulty ladder

Use this table to pick challenges that stretch you without overwhelming you.

| Level        | Skill focus                          | Example task                               |
|--------------|--------------------------------------|--------------------------------------------|
| Beginner     | DI, basic controller                 | Return a greeting from `GET /hello`        |
| Intermediate | Validation, JPA, exception handling  | CRUD with derived queries and `@Valid`     |
| Advanced     | Transactions, profiles, testing      | Money transfer that rolls back on failure  |

## Common mistakes

- **Field injection over constructors.** Prefer constructor injection — it makes dependencies explicit and beans testable without Spring.
- **Catching exceptions in the service to return `null`.** Let them propagate to `@RestControllerAdvice` so HTTP status codes stay correct.
- **Forgetting `@Transactional` on multi-write methods.** Without it, a mid-method failure leaves partial data.
- **Skipping slice tests.** Use `@WebMvcTest` for controllers and `@DataJpaTest` for repositories to keep tests fast and focused.

## Best practice: test the challenge

A challenge isn't finished until it's verified. A `@WebMvcTest` slice loads only the web layer:

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired MockMvc mvc;

    @Test
    void rejectsBlankName() throws Exception {
        mvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"\",\"email\":\"a@b.com\"}"))
           .andExpect(status().isBadRequest());
    }
}
```

**Summary:** Tackle Spring Boot challenges in small, layered slices — controller, service, repository — validating input and verifying each with focused slice tests. Climb the difficulty ladder, and avoid the field-injection and silent-catch pitfalls that quietly break real applications.
