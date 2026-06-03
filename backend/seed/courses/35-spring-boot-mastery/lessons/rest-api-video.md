# Video: Building REST APIs with Spring Boot

This video walks you through building a fully functional REST API with Spring Boot 3 — covering controllers, request mapping, JSON serialization, validation, and HTTP status codes in one focused session.

## What you'll learn

- Map HTTP verbs to handler methods with `@GetMapping`, `@PostMapping`, `@PutMapping`, and `@DeleteMapping`
- Bind path variables and query parameters using `@PathVariable` and `@RequestParam`
- Deserialize and validate JSON request bodies with `@RequestBody` and `@Valid` (Bean Validation)
- Return structured responses via `ResponseEntity<T>` with explicit HTTP status codes
- Organize endpoints cleanly under a base path with `@RequestMapping` at the class level
- Test endpoints interactively with Postman or `curl`

## Key takeaways

- `@RestController` combines `@Controller` and `@ResponseBody`, so every method return value is serialized to JSON automatically
- `ResponseEntity.ok(body)` vs `ResponseEntity.status(HttpStatus.CREATED).body(...)` gives precise control over status codes
- Bean Validation annotations (`@NotBlank`, `@Min`, `@Size`) on a DTO + `@Valid` on the parameter trigger automatic 400 responses for invalid input
- Keeping controller methods thin — delegating logic to a `@Service` — keeps the codebase maintainable

## Follow-along checklist

- [ ] Add `spring-boot-starter-web` and `spring-boot-starter-validation` to `pom.xml`
- [ ] Create a DTO record or class annotated with Bean Validation constraints
- [ ] Write a `@RestController` with at least one `@GetMapping` and one `@PostMapping`
- [ ] Return `ResponseEntity<YourDto>` with `HttpStatus.CREATED` from the POST handler
- [ ] Use `curl -X POST -H "Content-Type: application/json" -d '{"name":"Test"}' http://localhost:8080/api/items` to verify

The video link in this lesson opens a curated YouTube search featuring free, high-quality tutorials from channels like freeCodeCamp covering building REST APIs with Spring Boot end-to-end.
