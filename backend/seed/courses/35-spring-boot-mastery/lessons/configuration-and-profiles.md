# External Configuration and Profiles

Spring Boot's externalized configuration system lets you keep environment-specific values — database URLs, API keys, feature flags — outside of compiled code. The same JAR runs in development, staging, and production simply by supplying different property sources.

## Property Source Hierarchy

Spring Boot loads properties from multiple locations and merges them in a well-defined priority order (higher number wins):

| Priority | Source |
|---|---|
| 1 (lowest) | Default properties (`SpringApplication.setDefaultProperties`) |
| 2 | `application.properties` / `application.yaml` on the classpath |
| 3 | Profile-specific files: `application-{profile}.properties` |
| 4 | `application.properties` outside the JAR (same directory) |
| 5 | OS environment variables |
| 6 | JVM system properties (`-Dkey=value`) |
| 7 (highest) | Command-line arguments (`--key=value`) |

This means a value set in an environment variable always overrides the same key in `application.properties`, giving ops teams full control at deploy time without touching source files.

## application.properties vs application.yaml

Both formats are supported. Prefer `.yaml` for structured, nested config — it removes the repeated prefix noise:

```properties
# application.properties
spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
spring.datasource.username=app_user
spring.datasource.password=secret
spring.jpa.hibernate.ddl-auto=validate
```

```yaml
# application.yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: app_user
    password: secret
  jpa:
    hibernate:
      ddl-auto: validate
```

Both files in the same project are loaded; if a key appears in both, `.properties` wins by default.

## Binding Properties to a POJO with @ConfigurationProperties

Rather than scattering `@Value("${...}")` annotations everywhere, bind a whole group of related properties to a typed class:

```java
@ConfigurationProperties(prefix = "app.mail")
@Component
public class MailProperties {

    private String host;
    private int port = 587;
    private boolean startTlsEnabled = true;

    // standard getters and setters
    public String getHost() { return host; }
    public void setHost(String host) { this.host = host; }
    public int getPort() { return port; }
    public void setPort(int port) { this.port = port; }
    public boolean isStartTlsEnabled() { return startTlsEnabled; }
    public void setStartTlsEnabled(boolean startTlsEnabled) { this.startTlsEnabled = startTlsEnabled; }
}
```

```yaml
app:
  mail:
    host: smtp.example.com
    port: 465
    start-tls-enabled: false
```

Spring Boot automatically relaxes binding: `start-tls-enabled` (kebab-case) maps to `startTlsEnabled` (camelCase). Add the annotation processor to `pom.xml` to get IDE auto-completion:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-configuration-processor</artifactId>
    <optional>true</optional>
</dependency>
```

## Profiles

Profiles let you activate a named set of beans and properties. Activate a profile via:

```bash
# Command-line
java -jar app.jar --spring.profiles.active=prod

# Environment variable
export SPRING_PROFILES_ACTIVE=prod
```

### Profile-Specific Property Files

Create one file per environment alongside the base file:

```
src/main/resources/
  application.yaml          # shared defaults
  application-dev.yaml      # development overrides
  application-prod.yaml     # production overrides
```

```yaml
# application-dev.yaml
spring:
  datasource:
    url: jdbc:h2:mem:devdb
  jpa:
    show-sql: true
logging:
  level:
    root: DEBUG
```

```yaml
# application-prod.yaml
spring:
  datasource:
    url: ${DATABASE_URL}          # injected from env var at runtime
  jpa:
    show-sql: false
logging:
  level:
    root: WARN
```

### Profile-Specific Beans with @Profile

You can also restrict entire beans or `@Configuration` classes to a profile:

```java
@Configuration
@Profile("dev")
public class DevDataSeeder {

    @Bean
    CommandLineRunner seedDatabase(UserRepository repo) {
        return args -> {
            repo.save(new User("dev-admin@example.com", "Dev Admin"));
        };
    }
}
```

This bean is never created in `prod`, so seed data cannot leak into production.

## Reading a Single Value with @Value

For one-off values, `@Value` with a SpEL expression is concise:

```java
@Value("${app.feature.new-checkout:false}")
private boolean newCheckoutEnabled;
```

The `:false` after the colon is the default — the app starts even if the key is absent. Without a default, a missing key throws `IllegalArgumentException` at startup, which is often the desired behaviour for mandatory secrets.

## Common Mistakes and Best Practices

- **Committing secrets** — never put real passwords or API keys in `application.properties`. Use environment variables, a secrets manager, or Spring Cloud Config.
- **Using `application-default.yaml`** — this file activates when no profile is set; it can silently override your base `application.yaml`, which confuses teams.
- **Missing `@EnableConfigurationProperties`** — if you do not annotate the properties class with `@Component`, add `@EnableConfigurationProperties(MailProperties.class)` to any `@Configuration` class instead.
- **Relaxed binding pitfall** — `@Value("${app.mail.startTlsEnabled}")` does NOT use relaxed binding; write the exact key. Use `@ConfigurationProperties` when you need relaxed binding.
- **Multiple active profiles** — profiles are additive. `spring.profiles.active=base,prod` loads both files; later entries in the list win on conflicts.

Spring Boot's layered property system and first-class profile support give you a clean separation between code and configuration, making deployments predictable and environment-specific changes safe to audit.
