# Capstone Overview and Requirements

You have built REST controllers, persisted data with Spring Data JPA, secured endpoints, and written tests. The capstone ties it all together: you will design and ship a complete **Task Management API** using **Java 17+, Spring Boot 3, and Maven**. This lesson defines *what* you must build and *how* it will be graded. Later lessons walk through each slice.

## The project: "TaskFlow" API

A multi-user task tracker. Users register, authenticate, and manage tasks grouped into projects.

**Core requirements**

- CRUD for `Project` and `Task` resources via REST endpoints.
- Persistence with Spring Data JPA against PostgreSQL (H2 allowed for local dev/tests).
- Stateless JWT authentication with Spring Security; each user sees only their own data.
- Bean Validation (`jakarta.validation`) on all request DTOs.
- A global exception handler returning RFC-7807-style problem responses.
- Test coverage: slice tests plus at least one full integration test.

## Required endpoints

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| POST | `/api/auth/register` | Create account | Public |
| POST | `/api/auth/login` | Obtain JWT | Public |
| GET | `/api/projects` | List my projects | Bearer |
| POST | `/api/projects` | Create project | Bearer |
| GET | `/api/projects/{id}/tasks` | Tasks in a project | Bearer |
| POST | `/api/projects/{id}/tasks` | Add a task | Bearer |
| PATCH | `/api/tasks/{id}` | Update status/details | Bearer |
| DELETE | `/api/tasks/{id}` | Remove a task | Bearer |

## Entity sketch

Keep entities thin and let JPA manage relationships. A `Task` belongs to a `Project`, which belongs to a `User`.

```java
@Entity
@Table(name = "tasks")
public class Task {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TaskStatus status = TaskStatus.TODO;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "project_id")
    private Project project;

    // getters, setters, equals/hashCode on id
}
```

Always expose **DTOs**, never entities, from controllers. A Java `record` is ideal:

```java
public record CreateTaskRequest(
        @NotBlank @Size(max = 120) String title,
        String description) {
}
```

## Suggested dependencies (Maven)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

## Grading rubric

| Area | Weight | What we check |
|------|-------:|---------------|
| Functionality | 35% | All endpoints behave per the table |
| Security | 20% | JWT works; users isolated; no entity leaks |
| Data modeling | 15% | Correct relationships, constraints |
| Validation & errors | 15% | 400/404 returned with clear bodies |
| Testing | 15% | Slice + integration tests pass |

## Common mistakes to avoid

- **Returning entities directly** — causes lazy-loading `LazyInitializationException` and over-exposes the schema. Map to DTOs.
- **Forgetting ownership checks** — filter queries by the authenticated user; do not trust the path `id` alone.
- **Disabling CSRF without stateless config** — for a token API, set `SessionCreationPolicy.STATELESS` and disable CSRF deliberately.
- **No `spring.jpa.hibernate.ddl-auto` control** — use `validate` or Flyway in any environment beyond local prototyping.
- **Catching everything in controllers** — centralize with `@RestControllerAdvice`.

## Summary

The capstone is a secured, tested, multi-user TaskFlow API on Spring Boot 3. Build it slice by slice, expose DTOs, isolate user data, and let the rubric guide your priorities.
