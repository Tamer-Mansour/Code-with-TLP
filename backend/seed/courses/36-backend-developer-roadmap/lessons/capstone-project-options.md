# Capstone Project Options

Your capstone is the centerpiece of your portfolio. It should prove you can design a data model, build a secure REST API with Spring Boot, persist to MySQL, and expose a usable frontend. This lesson presents three realistic project options sized for the **Java 17 + Spring + MySQL 8 + HTML/CSS/JS** stack, plus guidance on choosing and scoping one.

## Three project options

| Project | Core entities | Standout skill it proves | Difficulty |
|---|---|---|---|
| Task / Project Tracker | User, Project, Task, Comment | CRUD, relationships, auth, filtering | Medium |
| Personal Finance Manager | User, Account, Transaction, Category | Aggregations, reporting, validation | Medium-High |
| Recipe & Meal Planner | User, Recipe, Ingredient, MealPlan | Many-to-many, search, file upload | Medium-High |

All three share the same backbone: secured endpoints, a relational schema, and a small JavaScript frontend that calls your API with `fetch`.

## A concrete slice

No matter which project you pick, the building blocks repeat. Here is the entity and schema for a `Task`:

```java
@Entity
@Table(name = "tasks")
public class Task {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Enumerated(EnumType.STRING)
    private Status status = Status.TODO;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    // getters and setters
}
```

The matching table in MySQL 8:

```sql
CREATE TABLE tasks (
    id         BIGINT       NOT NULL AUTO_INCREMENT,
    title      VARCHAR(200) NOT NULL,
    status     VARCHAR(20)  NOT NULL DEFAULT 'TODO',
    project_id BIGINT       NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_task_project FOREIGN KEY (project_id) REFERENCES projects (id)
) ENGINE=InnoDB;
```

A thin controller wires it to HTTP:

```java
@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    private final TaskService service;

    public TaskController(TaskService service) {
        this.service = service;
    }

    @GetMapping
    public List<TaskDto> list(@RequestParam(required = false) Status status) {
        return service.findAll(status);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public TaskDto create(@Valid @RequestBody CreateTaskRequest req) {
        return service.create(req);
    }
}
```

The frontend stays simple — vanilla ES6 is enough to demonstrate consuming the API:

```javascript
async function loadTasks() {
  const res = await fetch('/api/tasks?status=TODO');
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const tasks = await res.json();
  document.querySelector('#list').innerHTML =
    tasks.map(t => `<li>${t.title}</li>`).join('');
}
```

## Scope: what "done" means

Aim for a vertical slice that is complete, not a wide one that is shallow. A passing capstone should include:

- **Authentication** — JWT or session-based login via Spring Security.
- **At least 4 entities** with real relationships (one-to-many, many-to-many).
- **Validation** using `@Valid` and Bean Validation annotations.
- **A migration tool** (Flyway or Liquibase) so the schema is reproducible.
- **Tests** — at least a few `@SpringBootTest` / `@WebMvcTest` cases.
- **A README** with setup steps and screenshots.

## Common mistakes and best practices

- **Returning entities directly.** Map to DTOs; exposing JPA entities leaks lazy proxies and creates serialization loops.
- **Skipping migrations.** Relying on `ddl-auto=update` works on your machine and breaks everywhere else. Use Flyway and set `spring.jpa.hibernate.ddl-auto=validate`.
- **Over-scoping.** Three polished features beat ten half-built ones. Cut ruthlessly.
- **No environment config.** Read secrets from environment variables, never hard-code DB passwords in `application.properties`.
- **Ignoring error responses.** Add a `@ControllerAdvice` so clients get clean JSON errors, not stack traces.

**Summary:** Pick one focused project, build a secure end-to-end vertical slice (MySQL schema → Spring REST API → JS frontend), and prioritize correctness, validation, and a clear README over feature count.
