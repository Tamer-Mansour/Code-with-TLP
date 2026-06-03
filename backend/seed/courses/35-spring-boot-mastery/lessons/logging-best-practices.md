# Logging Best Practices

Logging is one of the most important observability tools in a production Spring Boot application. Done well, logs let you diagnose failures in seconds; done poorly, they either drown you in noise or leave you blind when something goes wrong. This lesson covers the right abstractions, configuration patterns, and habits that make logs genuinely useful.

## SLF4J + Logback: the default stack

Spring Boot ships with **Logback** as the default logging implementation and routes everything through the **SLF4J** facade. Never import a logging implementation directly — always program to the SLF4J API so you can swap implementations without touching application code.

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class OrderService {

    private static final Logger log = LoggerFactory.getLogger(OrderService.class);

    public Order placeOrder(OrderRequest request) {
        log.info("Placing order for customerId={} items={}", request.customerId(), request.items().size());

        Order order = processOrder(request);

        log.info("Order placed successfully orderId={} total={}", order.getId(), order.getTotal());
        return order;
    }
}
```

With Lombok on the classpath you can replace the boilerplate field with the `@Slf4j` annotation, which generates the exact same field at compile time:

```java
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class OrderService {
    // log field is injected by Lombok — use it directly
}
```

## Configuring log levels in application.properties

```properties
# Root level — keep at INFO in production
logging.level.root=INFO

# Your own packages can be more verbose during development
logging.level.com.example.orders=DEBUG

# Silence noisy third-party libraries
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.orm.jdbc.bind=TRACE
logging.level.org.springframework.security=WARN
```

Avoid `TRACE` on `root` in production — it generates gigabytes of output from Spring internals and degrades throughput.

## Log levels at a glance

| Level | When to use |
|-------|-------------|
| `ERROR` | Unrecoverable failure; an operator must investigate |
| `WARN` | Unexpected state the app handled gracefully; worth monitoring |
| `INFO` | Normal application lifecycle events (startup, shutdown, significant business events) |
| `DEBUG` | Developer-facing detail useful during troubleshooting |
| `TRACE` | Very fine-grained; only ever enabled temporarily |

A practical rule: `ERROR` and `WARN` should be actionable. If a `WARN` log fires constantly in normal operation, downgrade it to `DEBUG`.

## Structured logging with key=value pairs

Prefer key=value pairs over plain prose. They are easy to grep, parse by log aggregators (Datadog, Grafana Loki, ELK), and searchable without regex gymnastics.

```java
// Avoid: hard to parse programmatically
log.info("User 42 logged in from 192.168.1.5");

// Prefer: structured fields
log.info("User login userId={} ip={}", userId, ip);
```

For full JSON output in production, add the Logstash encoder to your `pom.xml`:

```xml
<dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>7.4</version>
</dependency>
```

Then configure a JSON appender in `src/main/resources/logback-spring.xml`:

```xml
<configuration>
    <springProfile name="prod">
        <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
            <encoder class="net.logstash.logback.encoder.LogstashEncoder"/>
        </appender>
        <root level="INFO">
            <appender-ref ref="JSON"/>
        </root>
    </springProfile>

    <springProfile name="!prod">
        <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
            <encoder>
                <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
            </encoder>
        </appender>
        <root level="DEBUG">
            <appender-ref ref="CONSOLE"/>
        </root>
    </springProfile>
</configuration>
```

Using `<springProfile>` keeps development logs human-readable while production logs are machine-parseable JSON.

## MDC: correlation IDs across log lines

The **Mapped Diagnostic Context (MDC)** lets you attach per-request context (like a correlation or trace ID) to every log line emitted within that request thread — without passing it through every method call.

```java
import org.slf4j.MDC;
import org.springframework.stereotype.Component;
import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import java.io.IOException;
import java.util.UUID;

@Component
public class CorrelationIdFilter implements Filter {

    private static final String CORRELATION_ID = "correlationId";

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, jakarta.servlet.ServletException {

        String correlationId = ((HttpServletRequest) request)
                .getHeader("X-Correlation-Id");
        if (correlationId == null || correlationId.isBlank()) {
            correlationId = UUID.randomUUID().toString();
        }

        MDC.put(CORRELATION_ID, correlationId);
        try {
            chain.doFilter(request, response);
        } finally {
            MDC.clear(); // always clear to avoid ThreadPool leaks
        }
    }
}
```

Include `%X{correlationId}` in your Logback pattern to print it on every line:

```xml
<pattern>%d{HH:mm:ss.SSS} [%X{correlationId}] %-5level %logger{36} - %msg%n</pattern>
```

## Common mistakes to avoid

- **Logging sensitive data.** Never log passwords, tokens, credit card numbers, or PII. Annotate sensitive fields and scrub them before they reach log statements.
- **String concatenation in log calls.** Use SLF4J's `{}` placeholders — the string is only built if the level is enabled, avoiding needless object allocation.
- **Swallowing exceptions.** `log.error("Failed")` without passing the exception loses the stack trace. Always write `log.error("Failed to process order orderId={}", id, ex)`.
- **One logger per class.** Avoid sharing a single static logger across packages; per-class loggers give precise source information and allow fine-grained level control.
- **Missing `MDC.clear()`.** Servlet containers reuse threads. Always clear the MDC in a `finally` block or you'll leak context from previous requests.

## Summary

Use SLF4J with structured `key=value` log messages, configure levels per package in `application.properties`, emit JSON in production via Logstash encoder, and attach correlation IDs through MDC — together these habits make your logs as useful in production as they are during development.
