# Beans and the Application Context

## What Is a Bean?

In Spring, a **bean** is any object whose lifecycle — creation, configuration, and destruction — is managed by the Spring IoC container. You do not call `new` yourself; instead, you describe what you need, and the container wires everything together.

Beans are the fundamental building blocks of every Spring application. Controllers, services, repositories, data sources, and message listeners are all beans.

## The Application Context

The `ApplicationContext` is Spring's IoC container. It reads your configuration (annotations, Java config classes, or XML), instantiates beans in the correct order, injects dependencies, and keeps the instances ready for use throughout the application lifetime.

Spring Boot creates and manages the `ApplicationContext` for you automatically when you call `SpringApplication.run(...)`.

```java
@SpringBootApplication
public class BookstoreApplication {

    public static void main(String[] args) {
        ApplicationContext ctx = SpringApplication.run(BookstoreApplication.class, args);

        // Retrieve a bean manually (rarely needed — prefer injection)
        BookService svc = ctx.getBean(BookService.class);
        System.out.println(svc.count() + " books loaded");
    }
}
```

## Defining Beans

### 1. Stereotype Annotations (most common)

Annotate a class and let Spring discover it through component scanning.

| Annotation | Typical Use |
|---|---|
| `@Component` | Generic bean — any managed component |
| `@Service` | Business/domain logic layer |
| `@Repository` | Data-access layer; also enables exception translation |
| `@Controller` / `@RestController` | Web layer (MVC / REST) |

```java
@Service
public class BookService {

    private final BookRepository repository;

    // Constructor injection — preferred over field injection
    public BookService(BookRepository repository) {
        this.repository = repository;
    }

    public long count() {
        return repository.count();
    }
}
```

Spring detects `@Service`, creates one instance, sees the constructor needs a `BookRepository`, finds that bean too, and injects it automatically. No XML, no manual wiring.

### 2. `@Bean` Methods Inside a `@Configuration` Class

Use this when you need to configure a third-party class you cannot annotate yourself.

```java
@Configuration
public class AppConfig {

    @Bean
    public ObjectMapper objectMapper() {
        return JsonMapper.builder()
                .addModule(new JavaTimeModule())
                .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
                .build();
    }
}
```

The method name (`objectMapper`) becomes the bean name by default.

## Bean Scope

By default every bean is a **singleton** — one shared instance per `ApplicationContext`. Other scopes exist for specific needs:

| Scope | Instances created | Typical use |
|---|---|---|
| `singleton` (default) | One per context | Services, repositories, config |
| `prototype` | One per `getBean()` call | Stateful helpers, command objects |
| `request` | One per HTTP request | Web layer state (Spring MVC) |
| `session` | One per HTTP session | User-scoped web data |

Declare a non-default scope with `@Scope`:

```java
@Component
@Scope("prototype")
public class ReportBuilder { ... }
```

## Bean Initialization and Destruction

You can hook into a bean's lifecycle:

```java
@Service
public class CacheWarmer {

    @PostConstruct          // runs after dependency injection completes
    public void load() {
        System.out.println("Cache warming...");
    }

    @PreDestroy             // runs before the context shuts down
    public void flush() {
        System.out.println("Cache flushed.");
    }
}
```

`@PostConstruct` and `@PreDestroy` are standard Jakarta EE annotations — no Spring import needed.

## Common Mistakes

- **Field injection with `@Autowired`** — works but hides dependencies, makes testing harder, and prevents `final` fields. Prefer constructor injection.
- **Circular dependencies** — Bean A needs B, B needs A. Spring can detect these at startup; fix them by refactoring or using `@Lazy` on one parameter.
- **Forgetting `@Configuration`** — A `@Bean` method in a plain class (no `@Configuration`) bypasses CGLIB proxying and will return a fresh instance on every call instead of the managed singleton.
- **Multiple beans of the same type** — Spring throws `NoUniqueBeanDefinitionException`. Qualify with `@Primary` or `@Qualifier("name")`.

```java
@Service
@Primary                        // used when no qualifier is specified
public class DefaultEmailSender implements EmailSender { ... }

@Service
@Qualifier("audit")
public class AuditEmailSender implements EmailSender { ... }
```

## Summary

The `ApplicationContext` is the heart of every Spring Boot application: it discovers beans through annotations or `@Configuration` classes, manages their full lifecycle, and injects dependencies so your code stays loosely coupled and easy to test. Understanding the singleton scope and preferring constructor injection are the two habits that prevent the most common wiring bugs.
