# Quiz: Production Readiness

Test your understanding of external configuration, Spring profiles, Spring Boot Actuator, structured
logging, executable JAR packaging, and Dockerizing a Spring Boot application for production deployment.

---

**Q1. A team uses the following `application.properties` and a profile-specific override file. Which property value is active when the application starts with `--spring.profiles.active=prod`?**

```properties
# application.properties
server.port=8080
app.feature.flag=false

# application-prod.properties
server.port=443
app.feature.flag=true
```

- [ ] `server.port=8080` and `app.feature.flag=false` — `application.properties` always takes precedence.
- [ ] `server.port=443` only; profile-specific files cannot override non-port properties.
- [x] `server.port=443` and `app.feature.flag=true` — profile-specific properties files override the base `application.properties` for matching keys.
- [ ] An `IllegalStateException` is thrown because the same key appears in two files.

---

**Q2. A developer wants to bind a group of related properties to a type-safe Java class. Which snippet correctly reads the `payment.*` namespace from `application.properties`?**

```java
// Option A
@ConfigurationProperties(prefix = "payment")
@Component
public class PaymentProperties {
    private String gateway;
    private int timeoutSeconds;
    // getters and setters ...
}

// Option B
@Value("${payment.*}")
public class PaymentProperties { }

// Option C
@PropertySource("payment")
public class PaymentProperties { }
```

```properties
payment.gateway=stripe
payment.timeout-seconds=30
```

- [x] Option A — `@ConfigurationProperties(prefix = "payment")` with a Spring-managed bean binds relaxed property names (kebab-case maps to camelCase) to the class fields.
- [ ] Option B — `@Value` supports wildcard namespace binding with `${}` syntax.
- [ ] Option C — `@PropertySource("payment")` injects all `payment.*` keys automatically.
- [ ] None of them compiles; `@ConfigurationProperties` requires Spring XML context.

---

**Q3. Which `application.properties` entry enables the Spring Boot Actuator `/actuator/health` endpoint and exposes all built-in endpoints over HTTP?**

```properties
# Which pair of properties is correct?
```

- [ ] `management.endpoints.enable=true` and `management.server.expose=*`
- [ ] `actuator.health.enabled=true` and `actuator.endpoints.web.expose=all`
- [ ] `spring.actuator.expose=true` and `management.endpoint.health.show-details=always`
- [x] `management.endpoints.web.exposure.include=*` and `management.endpoint.health.show-details=always`

---

**Q4. Examine the Actuator health response below. What does a `DOWN` component status in the composite health check cause the overall application status to be?**

```json
{
  "status": "DOWN",
  "components": {
    "db": {
      "status": "DOWN",
      "details": {
        "error": "Unable to acquire JDBC Connection"
      }
    },
    "diskSpace": {
      "status": "UP"
    }
  }
}
```

- [ ] The overall status remains `UP` as long as at least one component is healthy.
- [ ] The overall status becomes `UNKNOWN` until all components are checked again.
- [ ] Spring Boot throws a `HealthCheckException` and shuts the application down.
- [x] The overall status becomes `DOWN`, and the `/actuator/health` endpoint returns HTTP 503 Service Unavailable.

---

**Q5. A developer adds the Micrometer + Prometheus dependency and wants to expose application metrics. Which Actuator property enables the `/actuator/prometheus` endpoint, and what is the correct Maven dependency artifact ID?**

| Concern | Answer |
|---|---|
| Property to expose the endpoint | `management.endpoints.web.exposure.include=prometheus` |
| Maven artifact | `micrometer-registry-prometheus` |
| Group ID | `io.micrometer` |

Based on this table, which statement is correct?

- [ ] The Prometheus scrape endpoint is enabled by default with no extra dependency.
- [ ] The artifact group ID is `org.springframework.boot`, not `io.micrometer`.
- [ ] Setting `management.metrics.export.prometheus.enabled=true` alone exposes the endpoint without adding the dependency.
- [x] Both the `micrometer-registry-prometheus` dependency (`io.micrometer`) and `management.endpoints.web.exposure.include=prometheus` are required to expose metrics to a Prometheus scraper.

---

**Q6. Which logging configuration correctly sets the root log level to `WARN` and enables `DEBUG` level only for the `com.example.payment` package in `application.properties`?**

```properties
# Option A
logging.level.root=WARN
logging.level.com.example.payment=DEBUG

# Option B
log.root=WARN
log.package.com.example.payment=DEBUG

# Option C
spring.logging.root-level=warn
spring.logging.debug=com.example.payment

# Option D
logging.config=classpath:logback.xml
logging.level=com.example.payment:DEBUG
```

- [x] Option A — Spring Boot's `logging.level.<logger-name>` and `logging.level.root` are the correct property keys.
- [ ] Option B — the `log.*` namespace is what Spring Boot reads for log levels.
- [ ] Option C — Spring Boot uses `spring.logging.*` as the prefix for log-level properties.
- [ ] Option D — free-form `logging.level=<package>:<level>` syntax is what Spring Boot parses.

---

**Q7. You package the application with `mvn clean package` and inspect the resulting JAR. Which statement correctly describes the structure of a Spring Boot executable ("fat") JAR?**

```bash
jar tf target/myapp-1.0.0.jar | head -20
# BOOT-INF/classes/com/example/...
# BOOT-INF/lib/spring-core-6.1.0.jar
# BOOT-INF/lib/jackson-databind-2.16.0.jar
# META-INF/MANIFEST.MF
# org/springframework/boot/loader/...
```

- [ ] The fat JAR contains only your compiled classes; dependencies are fetched from Maven Central at runtime.
- [ ] `BOOT-INF/lib` holds source JARs; bytecode is compiled directly into `BOOT-INF/classes`.
- [ ] The JAR is an OSGi bundle; Spring Boot uses Felix as the embedded OSGi runtime.
- [x] The fat JAR embeds all dependency JARs under `BOOT-INF/lib/`, your compiled classes under `BOOT-INF/classes/`, and the Spring Boot Loader under `org/springframework/boot/loader/`, making it fully self-contained and runnable with `java -jar`.

---

**Q8. A developer writes the following `Dockerfile` for a Spring Boot application. Which layer-ordering problem does it have, and how should it be fixed?**

```dockerfile
# Problematic Dockerfile
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY target/myapp-1.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

- [ ] `EXPOSE 8080` must appear before `WORKDIR`; otherwise the port is never published.
- [ ] `eclipse-temurin:21-jre` is not a valid base image; only `openjdk:21` is accepted by Docker.
- [ ] The `ENTRYPOINT` form must use shell form (`ENTRYPOINT java -jar app.jar`) for signal handling.
- [x] Copying a single fat JAR means any source change invalidates the entire Docker layer. The fix is to use Spring Boot's layered JAR feature (`-Djarmode=layertools extract`) and copy dependency, snapshot, and application layers separately so that only changed layers are rebuilt.

---

**Q9. A team wants to pass the database password to the containerized Spring Boot app at runtime without baking it into the image. Which approach follows the twelve-factor app principle for secrets?**

```bash
# Approach A — bake into image
RUN echo "spring.datasource.password=s3cr3t" >> /app/application.properties

# Approach B — environment variable at runtime
docker run -e SPRING_DATASOURCE_PASSWORD=s3cr3t myapp:latest

# Approach C — Docker secret / Kubernetes Secret mounted as a file
# application.properties reads: spring.datasource.password=${DB_PASSWORD}
# and the container receives DB_PASSWORD from an injected secret
```

- [ ] Approach A is correct — embedding secrets in the image ensures they are always available.
- [ ] None of the approaches work; Spring Boot only reads passwords from a database credentials file named `db.credentials`.
- [x] Approaches B and C both follow twelve-factor principles. Spring Boot maps environment variable `SPRING_DATASOURCE_PASSWORD` (uppercase, dots replaced with underscores) to `spring.datasource.password` automatically via its relaxed binding rules.
- [ ] Approach B is invalid because Docker environment variables cannot contain passwords with special characters.

---

**Q10. Which Spring Boot property activates the `dev` and `local` profiles simultaneously when starting the application from the command line?**

```bash
java -jar myapp.jar ???
```

- [ ] `--spring.profiles.active=dev --spring.profiles.active=local` (two separate flags)
- [ ] `--spring.profile=dev,local`
- [ ] `--profiles.active=dev+local`
- [x] `--spring.profiles.active=dev,local` (a single comma-separated value activates multiple profiles)
