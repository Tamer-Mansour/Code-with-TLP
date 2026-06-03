# What's Next: Resources and Roadmap

You have built real, production-relevant Spring Boot 3 applications — REST APIs with validation, JPA persistence, JWT security, exception handling, and a full test suite. This lesson maps out the skills that naturally follow, points you to authoritative resources, and shows you how a Spring Boot project evolves from a coursework app into an enterprise-grade service.

## What You Now Know

Before looking ahead, take stock of the foundation you have built.

| Module completed | Core skills gained |
|---|---|
| Spring Core & DI | IoC container, bean lifecycle, `@Configuration`, profiles |
| Data Layer (JPA) | Entities, repositories, JPQL, pagination, transactions |
| REST APIs | Controllers, `ResponseEntity`, validation, exception handling |
| Security | Spring Security filter chain, JWT, method-level security |
| Testing | Unit tests with Mockito, `@WebMvcTest`, `@DataJpaTest`, integration tests |
| Operations | Actuator endpoints, Docker packaging |

## Immediate Next Steps

### 1. Spring Data and Persistence Depth

The course used H2 and basic CRUD. Production systems need more.

- Switch to **PostgreSQL** or **MySQL** and add **Flyway** (or Liquibase) for schema migrations.
- Learn Spring Data JPA projections and `@Query` with native SQL.
- Explore **Spring Data Redis** for caching frequently read data.

A minimal Flyway dependency addition:

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
```

```properties
# application.properties
spring.flyway.enabled=true
spring.flyway.locations=classpath:db/migration
```

Place migration scripts such as `V1__create_tasks.sql` under `src/main/resources/db/migration/`. Flyway runs them in order on startup and never re-runs an already-applied version.

### 2. Reactive Programming with Spring WebFlux

Spring Boot ships a second web stack based on Project Reactor. If you anticipate high concurrency with low thread overhead (streaming, chat, real-time dashboards), WebFlux is the path.

```java
// Reactive controller — note Mono and Flux instead of plain types
@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    private final TaskRepository repo; // extends ReactiveCrudRepository

    @GetMapping
    public Flux<Task> all() {
        return repo.findAll();
    }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<Task>> one(@PathVariable Long id) {
        return repo.findById(id)
                   .map(ResponseEntity::ok)
                   .defaultIfEmpty(ResponseEntity.notFound().build());
    }
}
```

The mental shift: instead of blocking calls, you compose reactive pipelines. Start with the official [Spring WebFlux docs](https://docs.spring.io/spring-framework/reference/web/webflux.html) and the Reactor reference guide.

### 3. Messaging and Event-Driven Services

REST is request-response. Real systems also need asynchronous messaging.

- **Spring for Apache Kafka** — ideal for high-throughput event streams.
- **Spring AMQP (RabbitMQ)** — straightforward pub/sub with durable queues.
- **Spring Events** (`ApplicationEventPublisher`) — lightweight in-process events, good for decoupling modules without adding infrastructure.

```java
// Publishing an in-process domain event
@Service
public class TaskService {
    private final ApplicationEventPublisher publisher;

    public Task complete(Long id) {
        Task task = find(id);
        task.setStatus(TaskStatus.DONE);
        Task saved = repo.save(task);
        publisher.publishEvent(new TaskCompletedEvent(saved));
        return saved;
    }
}
```

### 4. Cloud-Native Patterns

A containerised Spring Boot app is only the beginning of cloud readiness.

| Pattern | Spring Boot support |
|---|---|
| Externalized config | Spring Cloud Config Server / Kubernetes ConfigMaps |
| Service discovery | Spring Cloud Netflix Eureka / Kubernetes Services |
| Circuit breaker | Resilience4j via Spring Cloud Circuit Breaker |
| Distributed tracing | Micrometer Tracing + Zipkin / OTLP |
| Secrets management | Spring Vault / AWS Secrets Manager integration |

Add Resilience4j in one dependency block:

```xml
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-spring-boot3</artifactId>
    <version>2.2.0</version>
</dependency>
```

Then annotate a method with `@CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")` and configure thresholds in `application.yaml`.

### 5. Observability

Actuator exposed health and metrics. The next level is structured logging, distributed traces, and dashboards.

```yaml
# application.yaml — enable all actuator endpoints and structured JSON logs
management:
  endpoints:
    web:
      exposure:
        include: "*"
  tracing:
    sampling:
      probability: 1.0
logging:
  structured:
    format:
      console: ecs   # Elastic Common Schema — supported from Spring Boot 3.4
```

Pair this with a **Grafana + Prometheus + Loki** stack (all run locally with a single `docker compose up`) to visualise metrics and logs together.

## Authoritative Resources

| Resource | What it covers |
|---|---|
| [spring.io/guides](https://spring.io/guides) | Short, focused "Getting Started" guides for every Spring project |
| [Spring Boot Reference Docs](https://docs.spring.io/spring-boot/docs/current/reference/html/) | The definitive, always-current manual |
| [Baeldung.com](https://www.baeldung.com) | Practical tutorials with full code; search by Spring topic |
| [Spring Boot GitHub](https://github.com/spring-projects/spring-boot) | Source code, issues, release notes |
| *Spring Boot in Practice* (Manning) | Book with real-world recipes for Security, Actuator, cloud |
| *Cloud Native Spring in Action* (Manning) | Deep dive into Spring Cloud, Kubernetes, and resilience |

## Common Pitfalls to Avoid as You Go Deeper

- **N+1 queries** — use `@EntityGraph` or JOIN FETCH in JPQL instead of loading collections lazily in a loop.
- **Exposing entities directly** — always map to response DTOs before leaving the service layer.
- **Ignoring thread safety** — Spring beans are singletons; never store mutable request state in a field.
- **Skipping contract tests** — as you split services, use Spring Cloud Contract or Pact to prevent API drift between consumers and providers.
- **Hardcoding secrets** — externalise all credentials from day one; use `spring.config.import=optional:vault://` or environment variables.

## Your Learning Roadmap at a Glance

```
Spring Boot Mastery (done)
    |
    +-- Flyway + PostgreSQL         (add to any project this week)
    |
    +-- Spring WebFlux              (new project, ~2 weeks)
    |
    +-- Kafka / RabbitMQ messaging  (extend an existing project, ~1 week)
    |
    +-- Spring Cloud (Config, Discovery, Circuit Breaker)  (~3 weeks)
    |
    +-- Kubernetes deployment       (pair with Docker knowledge you have)
    |
    +-- Observability (Micrometer Tracing, Grafana stack)  (~1 week)
```

Work through the steps in order — each builds on the last, and you already have the Spring Boot foundation to understand every piece.

---

Completing this course gives you a solid, production-relevant Spring Boot 3 skill set; following the roadmap above will take you from application developer to cloud-native engineer capable of building, securing, testing, and operating distributed Java services at scale.
