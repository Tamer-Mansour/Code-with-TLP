# Async Methods and Scheduled Tasks

Spring Boot makes it straightforward to run work off the main thread and to trigger code on a timer. Two annotations carry most of the weight: `@Async` for non-blocking method calls and `@Scheduled` for recurring jobs.

## Enabling the features

Both features are opt-in. Add the enablers to any `@Configuration` class (or your main class):

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

@Configuration
@EnableAsync
@EnableScheduling
public class AsyncConfig {
}
```

Without `@EnableAsync`, `@Async` methods run synchronously — a silent, easy-to-miss mistake.

## Async methods with @Async

Annotate a `public` method with `@Async` to execute it in a separate thread from Spring's task executor pool. The caller returns immediately.

```java
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Service
public class EmailService {

    @Async
    public void sendWelcomeEmail(String to) {
        // Simulates a slow SMTP call — runs in a worker thread.
        System.out.println("Sending email to " + to + " on thread: "
                + Thread.currentThread().getName());
        // ... JavaMailSender logic here ...
    }
}
```

The controller that calls `sendWelcomeEmail()` gets back immediately; the email is sent in the background.

### Returning a result from an async method

If you need the result later, return `CompletableFuture<T>` instead of `void`:

```java
import java.util.concurrent.CompletableFuture;

@Async
public CompletableFuture<String> fetchReport(Long id) {
    String report = expensiveComputation(id);
    return CompletableFuture.completedFuture(report);
}
```

The caller can then `.join()` or chain callbacks on the future without blocking the request thread needlessly.

### Configuring the thread pool

By default, Spring uses a simple `SimpleAsyncTaskExecutor` that creates a new thread per call — **not suitable for production**. Define a real pool:

```java
import org.springframework.context.annotation.Bean;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import java.util.concurrent.Executor;

@Configuration
@EnableAsync
@EnableScheduling
public class AsyncConfig {

    @Bean(name = "taskExecutor")
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(4);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(50);
        executor.setThreadNamePrefix("async-worker-");
        executor.initialize();
        return executor;
    }
}
```

Point a specific method at a named executor: `@Async("taskExecutor")`.

## Scheduled tasks with @Scheduled

Place `@Scheduled` on a `void` method in any Spring-managed bean to run it automatically.

```java
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class ReportJob {

    // Runs every day at 02:00 AM server time.
    @Scheduled(cron = "0 0 2 * * *")
    public void generateDailyReport() {
        System.out.println("Generating report at " + java.time.LocalDateTime.now());
    }

    // Runs 5 seconds after the previous execution finishes.
    @Scheduled(fixedDelay = 5000)
    public void pollExternalApi() {
        // ...
    }

    // Runs every 10 seconds measured from startup.
    @Scheduled(fixedRate = 10_000)
    public void syncCache() {
        // ...
    }
}
```

### Scheduling options compared

| Attribute | Meaning | Example |
|---|---|---|
| `cron` | Cron expression (second, minute, hour, day, month, weekday) | `"0 30 8 * * MON-FRI"` — 8:30 AM weekdays |
| `fixedRate` | Milliseconds between **start** times | `fixedRate = 60_000` |
| `fixedDelay` | Milliseconds between **end** of last run and start of next | `fixedDelay = 30_000` |
| `initialDelay` | Delay before the very first execution | `initialDelay = 5000` |

Prefer `fixedDelay` over `fixedRate` when a task may sometimes run longer than its interval, to avoid overlapping executions.

### Externalising the schedule

Hard-coding intervals in annotations makes tuning difficult. Use property placeholders instead:

```java
@Scheduled(cron = "${jobs.report.cron:0 0 2 * * *}")
public void generateDailyReport() { ... }
```

```properties
# application.properties
jobs.report.cron=0 0 3 * * *
```

## Common mistakes and best practices

- **Self-invocation breaks `@Async`.** Calling an async method from the same bean bypasses the proxy and runs synchronously. Move the method to a separate bean.
- **`private` methods are ignored.** Both `@Async` and `@Scheduled` require `public` methods to work through the proxy.
- **Uncaught exceptions in `@Async` are swallowed** unless you set an `AsyncUncaughtExceptionHandler`. Register one via `AsyncConfigurer` to log or alert on failures.
- **`@Scheduled` is single-threaded by default.** All scheduled tasks share one thread, so a slow task can delay others. Inject a `TaskScheduler` bean with a pool if tasks need to run concurrently.
- **Do not block scheduled methods indefinitely** — they hold the scheduler thread and starve other jobs.

## Summary

`@Async` offloads slow work to a thread pool, keeping request threads responsive, while `@Scheduled` drives time-based jobs without an external cron daemon. Enable both with `@EnableAsync` / `@EnableScheduling`, configure a proper `ThreadPoolTaskExecutor` for production, and externalise cron expressions to properties for easy tuning without redeployment.
