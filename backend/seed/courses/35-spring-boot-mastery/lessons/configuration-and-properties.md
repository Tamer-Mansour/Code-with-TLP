# External Configuration and Profiles

A production app must run in many environments — your laptop, CI, staging, production — without code
changes. Spring Boot solves this with **externalized configuration**: values live outside the code in
property files, environment variables, and command-line arguments, and Spring binds them into your beans.

## Property sources and precedence

Spring Boot reads configuration from many sources and merges them. Later (higher-priority) sources
**override** earlier ones. A simplified order, highest priority last:

| Source                                   | Example                                  |
|------------------------------------------|------------------------------------------|
| `application.properties` / `.yml`        | packaged defaults                        |
| Profile-specific files                   | `application-prod.yml`                    |
| OS environment variables                 | `SERVER_PORT=9000`                        |
| Command-line arguments                   | `--server.port=9000`                      |

This means you can ship sane defaults in `application.yml` and override only what differs per
environment — without rebuilding the jar.

## Defining properties

`src/main/resources/application.yml`:

```yaml
server:
  port: 8080

app:
  name: Task API
  page-size: 25
  feature:
    signups-enabled: true
```

## Reading configuration

For a single value, use `@Value`:

```java
@Value("${app.page-size}")
private int pageSize;
```

For a group of related values, prefer **type-safe** `@ConfigurationProperties` — it binds a whole
prefix to a class, with validation and IDE support:

```java
@Component
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String name;
    private int pageSize = 20;       // default if not set
    private Feature feature = new Feature();
    // getters & setters required for binding
    public static class Feature {
        private boolean signupsEnabled;
        // getter/setter
    }
}
```

Inject `AppProperties` anywhere like any other bean. Relaxed binding means `page-size`, `pageSize`,
and `PAGE_SIZE` (env var) all map to the same field.

## Profiles

A **profile** is a named set of configuration activated for a particular environment.

```yaml
# application-dev.yml — H2, verbose logging
spring:
  datasource:
    url: jdbc:h2:mem:devdb
logging:
  level:
    org.springframework.web: DEBUG
```

```yaml
# application-prod.yml — real MySQL, lean logging
spring:
  datasource:
    url: jdbc:mysql://db:3306/tasks
logging:
  level:
    root: WARN
```

Activate a profile via property or env var:

```bash
java -jar app.jar --spring.profiles.active=prod
# or
export SPRING_PROFILES_ACTIVE=prod
```

Beans can be profile-scoped too:

```java
@Bean
@Profile("dev")
CommandLineRunner seedData(TaskRepository repo) {
    return args -> repo.save(new Task("Try the dev seed"));
}
```

## Keeping secrets out of the repo

Never commit passwords or API keys. Inject them as environment variables and reference them with a
placeholder (with an optional default):

```yaml
spring:
  datasource:
    password: ${DB_PASSWORD}
app:
  api-key: ${API_KEY:changeme}
```

## Common mistakes

- **Hardcoding environment values** in code instead of `application.yml` — defeats externalization.
- **Forgetting getters/setters** on a `@ConfigurationProperties` class — binding silently leaves
  fields null.
- **Committing secrets** to `application.yml` — use env vars or a secrets manager.
- Putting a profile-only bean in the default profile and wondering why prod seeds test data.

## Summary

Externalize everything that changes per environment, bind it type-safely with
`@ConfigurationProperties`, isolate environment differences in `application-<profile>.yml`, and feed
secrets through environment variables — never the jar.
