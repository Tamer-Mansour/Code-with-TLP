# Actuator, Health Checks, and Metrics

Spring Boot Actuator adds **production-ready endpoints** to your application with a single dependency — no boilerplate wiring required. It exposes information about health, environment, configuration, metrics, and more over HTTP (or JMX), giving you an instant operations dashboard.

## Adding Actuator

Add the starter to `pom.xml`:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

That is all that is needed to get a working `/actuator` base path. Restart the app and visit `http://localhost:8080/actuator` — you will see a list of enabled endpoints in JSON.

## Configuring Which Endpoints Are Exposed

By default, only `health` is exposed over HTTP. You control exposure in `application.properties` (or `application.yml`):

```properties
# Expose all built-in endpoints over HTTP
management.endpoints.web.exposure.include=*

# Or expose only specific ones
# management.endpoints.web.exposure.include=health,info,metrics,env

# Change the base path (default is /actuator)
management.endpoints.web.base-path=/manage

# Run the management server on a separate port (recommended in production)
management.server.port=8081
```

Running the management server on a **dedicated port** means your operational endpoints are never reachable through the public-facing port — a simple but powerful security boundary.

## The /health Endpoint

`/actuator/health` reports whether the application is ready to serve traffic. Spring Boot auto-detects components such as the database, disk space, and message brokers and creates `HealthIndicator` beans for each.

A typical response when the database is up:

```json
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": {
        "database": "PostgreSQL",
        "validationQuery": "isValid()"
      }
    },
    "diskSpace": {
      "status": "UP",
      "details": {
        "total": 499963174912,
        "free": 320489979904,
        "threshold": 10485760,
        "exists": true
      }
    }
  }
}
```

Show component-level detail by setting:

```properties
management.endpoint.health.show-details=always
# Options: never | when-authorized | always
```

### Writing a Custom HealthIndicator

```java
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

@Component
public class PaymentGatewayHealthIndicator implements HealthIndicator {

    private final PaymentGatewayClient client;

    public PaymentGatewayHealthIndicator(PaymentGatewayClient client) {
        this.client = client;
    }

    @Override
    public Health health() {
        try {
            boolean reachable = client.ping();
            if (reachable) {
                return Health.up()
                        .withDetail("gateway", "reachable")
                        .build();
            }
            return Health.down()
                    .withDetail("gateway", "timeout")
                    .build();
        } catch (Exception ex) {
            return Health.down(ex).build();
        }
    }
}
```

Spring Boot automatically registers this bean and includes a `paymentGateway` component under `/actuator/health`.

## Liveness and Readiness Probes

Kubernetes and other orchestrators use two distinct probes:

| Probe | Endpoint | Meaning |
|-------|----------|---------|
| Liveness | `/actuator/health/liveness` | App is alive; restart if DOWN |
| Readiness | `/actuator/health/readiness` | App can serve traffic; remove from LB if DOWN |

Enable them explicitly:

```properties
management.endpoint.health.probes.enabled=true
```

Spring Boot maps its internal `LivenessState` and `ReadinessState` to these paths automatically. For cloud deployments this is all the configuration you typically need.

## Metrics with Micrometer

Actuator ships with [Micrometer](https://micrometer.io/) as its metrics facade. Micrometer is vendor-neutral: you write metrics code once and choose a backend (Prometheus, Datadog, InfluxDB, CloudWatch, etc.) by adding the right dependency.

Browse all registered metric names at `/actuator/metrics`, then drill into a specific one:

```
GET /actuator/metrics/jvm.memory.used
GET /actuator/metrics/http.server.requests
GET /actuator/metrics/hikaricp.connections.active
```

### Exposing Metrics to Prometheus

Add the Prometheus registry:

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

Expose the scrape endpoint:

```properties
management.endpoints.web.exposure.include=health,info,metrics,prometheus
```

Prometheus then scrapes `http://your-host:8081/actuator/prometheus` on a configurable interval.

### Recording a Custom Metric

```java
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.stereotype.Service;

@Service
public class OrderService {

    private final Counter ordersPlaced;

    public OrderService(MeterRegistry registry) {
        this.ordersPlaced = Counter.builder("orders.placed")
                .description("Total number of orders placed")
                .tag("channel", "web")
                .register(registry);
    }

    public Order placeOrder(OrderRequest request) {
        // ... business logic ...
        ordersPlaced.increment();
        return savedOrder;
    }
}
```

The counter is immediately visible at `/actuator/metrics/orders.placed` and in the Prometheus scrape output.

## Common Mistakes and Best Practices

- **Never expose all endpoints publicly.** Use a dedicated management port (`management.server.port`) and restrict it at the network or firewall level.
- **Secure sensitive endpoints.** `env` and `heapdump` can leak secrets. Restrict them with Spring Security on the management port, or exclude them entirely via `management.endpoints.web.exposure.exclude`.
- **Do not implement heavy logic in `HealthIndicator.health()`.** Health checks are called frequently; keep them fast and idempotent, with a short timeout.
- **Use tags on metrics.** A counter named `orders.placed` with a `status` tag (`success`/`failure`) is far more useful than two separate counter names.
- **Prefer `@Timed` on controllers for HTTP latency** — Micrometer's `@Timed` annotation automatically creates histogram/summary metrics on annotated request-mapping methods.

## Summary

Spring Boot Actuator turns any application into a self-describing, production-observable service: `/health` feeds orchestrator probes and dashboards, and Micrometer metrics integrate seamlessly with Prometheus or any other monitoring backend with a single dependency swap.
