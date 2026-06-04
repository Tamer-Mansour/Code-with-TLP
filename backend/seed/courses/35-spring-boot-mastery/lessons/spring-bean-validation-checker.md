# Exercise: Bean Validation Rule Checker

Jakarta Bean Validation (used in Spring Boot 3+ via `spring-boot-starter-validation`) lets you annotate fields with constraints and then validate objects automatically in controllers with `@Valid`. This exercise asks you to build a simplified validation engine that evaluates the same categories of constraints.

## What you need to implement

Simulate a validation engine that:

1. Reads a set of field validation rules (`NOT_BLANK`, `MIN`, `MAX`, `SIZE_MIN`, `SIZE_MAX`).
2. Reads multiple test objects, each providing a value for every field.
3. For each object, checks all rules in order and reports which ones fail.

## Real-world connection

In Spring Boot, you declare constraints directly on a DTO class:

```java
public class RegisterRequest {

    @NotBlank
    @Size(min = 3, max = 20)
    private String username;

    @Min(18)
    private int age;
}
```

Then in your controller:

```java
@PostMapping("/register")
public ResponseEntity<Void> register(@Valid @RequestBody RegisterRequest req) {
    // only reached if all constraints pass
}
```

When validation fails, Spring throws `MethodArgumentNotValidException`, which your `@ControllerAdvice` can catch and transform into a `400 Bad Request` response with a list of field errors — exactly what this exercise models.

> **Note:** Jakarta Bean Validation uses the `jakarta.validation.*` namespace (Spring Boot 3+). Never use `javax.validation.*` in new Spring Boot 3 / 4 code.

## Input format

```
N
fieldName constraint value
...
T
fieldName fieldValue
...  (N lines per test object, repeated T times)
```

Constraints:
- `NOT_BLANK` — field value must not be empty or whitespace (the `value` column is `-`, ignored).
- `MIN int` — numeric value must be >= int.
- `MAX int` — numeric value must be <= int.
- `SIZE_MIN int` — string length must be >= int.
- `SIZE_MAX int` — string length must be <= int.

## Output format

For each test object, print `VALID` if all constraints pass, or one line per failing constraint in the order the rules were defined:
```
fieldName: CONSTRAINT violated
```

## Example

**Input:**
```
4
username NOT_BLANK -
username SIZE_MIN 3
username SIZE_MAX 20
age MIN 18
3
username alice
age 25
username ab
age 15
username
age 20
```

**Output:**
```
VALID
username: SIZE_MIN violated
age: MIN violated
username: NOT_BLANK violated
username: SIZE_MIN violated
```

Note that the third object (`username` blank, `age 20`) triggers both `NOT_BLANK` and `SIZE_MIN` violations because all applicable rules are checked independently — exactly how Jakarta Bean Validation evaluates every constraint on the field.

## Further reading

- [Building REST Services with Spring (Baeldung PDF)](https://www.baeldung.com/wp-content/uploads/2013/09/Building-REST-Services-with-Spring.pdf) — covers validation and error handling end-to-end
- [Spring Boot Reference — Validation](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
