# Project: Task Management API

## Overview

In this capstone project for the **Validation & Error Handling** module, you'll build a production-style **Task Management REST API** with Spring Boot 3. The API lets clients create, list, update, and delete tasks while enforcing strict input validation and returning consistent, well-structured error responses.

This project matters because real APIs live or die on how they handle *bad* input, not just the happy path. A task with a blank title, a due date in the past, or an unknown status should never reach your database — it should be rejected with a clear, machine-readable error. By the end, you'll have a service that validates requests with Jakarta Bean Validation and centralizes error handling with `@RestControllerAdvice`, producing RFC 7807-style problem responses.

## Learning Objectives

By completing this project you will be able to:

- Model a domain entity with JPA and map it to a relational table.
- Apply Jakarta Bean Validation annotations (`@NotBlank`, `@Size`, `@FutureOrPresent`, `@NotNull`) to DTOs.
- Trigger validation in controllers with `@Valid` and read binding results.
- Centralize exception handling using `@RestControllerAdvice` and `@ExceptionHandler`.
- Return consistent error payloads (field errors, status, timestamp) with correct HTTP status codes.
- Write a custom exception (`TaskNotFoundException`) and map it to `404 Not Found`.

## Prerequisites & Setup

You need **JDK 17+**, **Maven 3.8+**, and an IDE. We'll use the in-memory **H2** database so there's nothing extra to install.

Generate the project skeleton with Spring Initializr via curl:

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web,data-jpa,validation,h2 \
  -d type=maven-project \
  -d javaVersion=17 \
  -d bootVersion=3.2.5 \
  -d groupId=com.tlp \
  -d artifactId=task-api \
  -d name=task-api \
  -d packageName=com.tlp.taskapi \
  -o task-api.zip
unzip task-api.zip -d task-api && cd task-api
./mvnw spring-boot:run
```

Configure H2 in `src/main/resources/application.properties`:

```properties
spring.datasource.url=jdbc:h2:mem:tasks
spring.jpa.hibernate.ddl-auto=update
spring.h2.console.enabled=true
```

## Requirements

The service exposes CRUD endpoints for tasks. A task has a title, optional description, a status, and a due date.

| Method | Path           | Body          | Success | Errors                |
|--------|----------------|---------------|---------|-----------------------|
| POST   | `/api/tasks`   | TaskRequest   | 201     | 400 (validation)      |
| GET    | `/api/tasks`   | —             | 200     | —                     |
| GET    | `/api/tasks/{id}` | —          | 200     | 404                   |
| PUT    | `/api/tasks/{id}` | TaskRequest | 200    | 400, 404              |
| DELETE | `/api/tasks/{id}` | —          | 204     | 404                   |

**Validation rules**: title is required, 3–100 chars; description is optional, max 500 chars; status must be one of `TODO`, `IN_PROGRESS`, `DONE`; due date must be today or in the future.

## Step-by-Step Tasks

### 1. Define the entity and status enum

- [ ] Create a `TaskStatus` enum with `TODO`, `IN_PROGRESS`, `DONE`.
- [ ] Create the `Task` JPA entity.

```java
@Entity
@Table(name = "tasks")
public class Task {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String title;
    private String description;
    @Enumerated(EnumType.STRING)
    private TaskStatus status;
    private LocalDate dueDate;
    // getters and setters
}
```

### 2. Build the request DTO with validation

- [ ] Create `TaskRequest` with Bean Validation annotations.
- [ ] Keep the entity free of validation concerns (validate the DTO, not the entity).

```java
public record TaskRequest(
    @NotBlank @Size(min = 3, max = 100) String title,
    @Size(max = 500) String description,
    @NotNull TaskStatus status,
    @NotNull @FutureOrPresent LocalDate dueDate
) {}
```

### 3. Create the repository and service

- [ ] Extend `JpaRepository<Task, Long>`.
- [ ] In the service, throw `TaskNotFoundException` when an id is missing.

```java
public interface TaskRepository extends JpaRepository<Task, Long> {}

public class TaskNotFoundException extends RuntimeException {
    public TaskNotFoundException(Long id) {
        super("Task not found: " + id);
    }
}
```

### 4. Implement the controller

- [ ] Annotate the POST/PUT bodies with `@Valid`.
- [ ] Return `201 Created` with a `Location` header on create.

```java
@RestController
@RequestMapping("/api/tasks")
public class TaskController {
    private final TaskService service;
    public TaskController(TaskService service) { this.service = service; }

    @PostMapping
    public ResponseEntity<Task> create(@Valid @RequestBody TaskRequest req) {
        Task saved = service.create(req);
        return ResponseEntity
            .created(URI.create("/api/tasks/" + saved.getId()))
            .body(saved);
    }

    @GetMapping("/{id}")
    public Task getOne(@PathVariable Long id) {
        return service.findById(id); // throws TaskNotFoundException
    }
}
```

### 5. Centralize error handling

- [ ] Create a `@RestControllerAdvice` class.
- [ ] Handle `MethodArgumentNotValidException` → `400` with per-field messages.
- [ ] Handle `TaskNotFoundException` → `404`.

```java
@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Map<String, Object> onValidation(MethodArgumentNotValidException ex) {
        Map<String, String> fields = new HashMap<>();
        ex.getBindingResult().getFieldErrors()
            .forEach(e -> fields.put(e.getField(), e.getDefaultMessage()));
        return Map.of(
            "timestamp", Instant.now().toString(),
            "status", 400,
            "errors", fields
        );
    }

    @ExceptionHandler(TaskNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public Map<String, Object> onNotFound(TaskNotFoundException ex) {
        return Map.of(
            "timestamp", Instant.now().toString(),
            "status", 404,
            "message", ex.getMessage()
        );
    }
}
```

### 6. Verify the behavior manually

- [ ] Start the app and POST an invalid task; confirm a `400` with field errors.
- [ ] Create a valid task and re-fetch it by id.

```bash
# Invalid: blank title, past date -> 400
curl -i -X POST http://localhost:8080/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"","status":"TODO","dueDate":"2020-01-01"}'
```

A rejected request returns something like:

```json
{
  "timestamp": "2026-06-03T10:15:30Z",
  "status": 400,
  "errors": {
    "title": "must not be blank",
    "dueDate": "must be a date in the present or in the future"
  }
}
```

## Acceptance Criteria

- [ ] `POST /api/tasks` with valid data returns `201` and a `Location` header.
- [ ] Invalid input returns `400` with a per-field `errors` object.
- [ ] `GET /api/tasks/{id}` for an unknown id returns `404`, not `500`.
- [ ] `DELETE /api/tasks/{id}` returns `204` on success.
- [ ] `status` is persisted as a string (`EnumType.STRING`), not an ordinal.
- [ ] Validation lives on the DTO; the controller uses `@Valid`.
- [ ] All error responses share a consistent shape (timestamp + status).

## Stretch Challenges

1. **Pagination & filtering**: support `GET /api/tasks?status=TODO&page=0&size=10` using `Pageable`.
2. **Custom validator**: write a `@ValidStatusTransition` constraint that blocks moving a task from `DONE` back to `TODO`.
3. **RFC 7807**: return responses using Spring's `ProblemDetail` instead of an ad-hoc map.
4. **Response DTOs**: stop exposing the entity directly; map to a `TaskResponse` record.
5. **Tests**: add `@WebMvcTest` slice tests asserting the `400` and `404` bodies with MockMvc.

## Hints

- Bean Validation only fires when the parameter is annotated with `@Valid` (or `@Validated`); forgetting it silently skips validation.
- `MethodArgumentNotValidException` is thrown for `@RequestBody @Valid` failures; `ConstraintViolationException` is thrown for `@PathVariable`/`@RequestParam` validation — handle them separately if you validate query params.
- Use `EnumType.STRING` so adding a new status later doesn't corrupt existing rows.
- Keep the advice class free of business logic — it only translates exceptions into HTTP responses.
- Test the H2 console at `http://localhost:8080/h2-console` (JDBC URL `jdbc:h2:mem:tasks`) to inspect persisted rows.
