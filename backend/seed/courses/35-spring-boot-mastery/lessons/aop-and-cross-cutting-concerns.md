# Aspect-Oriented Programming

Some logic doesn't belong to any single class — logging, security checks, transaction management, and performance timing all repeat across many methods. These are **cross-cutting concerns**. Aspect-Oriented Programming (AOP) lets you keep them in one place instead of scattering them through your codebase.

Spring AOP is built into the framework and works seamlessly with Spring Boot 3 and Java 17+.

## Core Vocabulary

| Term | Meaning |
|------|---------|
| **Aspect** | A module that bundles a cross-cutting concern (e.g. `LoggingAspect`). |
| **Join point** | A point during execution where an aspect can apply — in Spring AOP, always a method execution. |
| **Advice** | The action taken at a join point (`@Before`, `@After`, `@Around`, etc.). |
| **Pointcut** | An expression that selects which join points the advice runs on. |
| **Weaving** | Linking aspects to target objects — Spring does this at runtime via proxies. |

## Enabling AOP

Add the starter to `pom.xml`. With Spring Boot, AOP auto-configuration activates automatically when the dependency is present.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-aop</artifactId>
</dependency>
```

## A Logging Aspect

This aspect logs every call to public methods in the `service` package, including timing.

```java
package com.tlp.shop.aspect;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class LoggingAspect {

    private static final Logger log = LoggerFactory.getLogger(LoggingAspect.class);

    @Around("execution(* com.tlp.shop.service..*(..))")
    public Object logExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();
        String method = joinPoint.getSignature().toShortString();
        log.info("Entering {}", method);
        try {
            Object result = joinPoint.proceed();   // run the actual method
            return result;
        } finally {
            long elapsed = System.currentTimeMillis() - start;
            log.info("Exiting {} ({} ms)", method, elapsed);
        }
    }
}
```

The pointcut `execution(* com.tlp.shop.service..*(..))` reads as: any return type (`*`), any class in `service` and sub-packages (`..`), any method, any arguments (`(..)`).

## Custom Annotation + Advice

A cleaner approach is to target methods by annotation rather than package. Define a marker:

```java
package com.tlp.shop.aspect;

import java.lang.annotation.*;

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Audited {
}
```

Then advise any method that carries it:

```java
@Aspect
@Component
public class AuditAspect {

    @AfterReturning(pointcut = "@annotation(com.tlp.shop.aspect.Audited)",
                    returning = "result")
    public void audit(JoinPoint jp, Object result) {
        System.out.println("Audited " + jp.getSignature().getName()
                + " -> " + result);
    }
}
```

Annotate a service method with `@Audited` and the advice fires automatically.

## Advice Types

- **`@Before`** — runs before the method.
- **`@AfterReturning`** — runs after a successful return; can read the return value.
- **`@AfterThrowing`** — runs only if the method throws.
- **`@After`** — runs always (like a `finally`).
- **`@Around`** — wraps the call; you decide whether and when to `proceed()`. The most powerful.

## Common Mistakes and Best Practices

- **Self-invocation doesn't work.** Spring AOP uses proxies, so a method calling another method *in the same bean* bypasses the proxy and the advice never runs. Call through an injected reference instead.
- **Only Spring-managed beans are advised.** Objects you create with `new` are invisible to AOP.
- **`@Around` advice must return** the result of `proceed()` (or your own value) — forgetting this returns `null` and breaks callers.
- Keep pointcut expressions in named methods (`@Pointcut`) to reuse and document them.
- Don't put heavy business logic in aspects; they're for concerns *around* logic, not the logic itself.

## Summary

AOP centralizes cross-cutting concerns like logging, auditing, and timing using aspects, pointcuts, and advice. In Spring Boot, add `spring-boot-starter-aop`, annotate a `@Component` with `@Aspect`, and target methods via `execution(...)` pointcuts or custom annotations — keeping your core code clean and focused.
