# What Is Spring Boot?

Spring Boot is an opinionated, convention-over-configuration layer built on top of the Spring Framework. It removes the XML files, manual bean wiring, and server setup that made traditional Spring projects notoriously tedious to bootstrap — letting you go from zero to a running HTTP server in under two minutes.

## The Problem Spring Boot Solves

Plain Spring requires explicit configuration for almost everything: declare every bean, set up a `DispatcherServlet`, configure a `DataSource`, drop a WAR into an external Tomcat instance. For a small CRUD API this could mean hundreds of lines of boilerplate before a single business rule is written.

Spring Boot inverts that default:

- **Auto-configuration** — detects JARs on the classpath and wires sensible defaults automatically.
- **Embedded server** — packages Tomcat (or Jetty/Undertow) inside the JAR; no external container needed.
- **Starter dependencies** — curated Maven/Gradle coordinates that pull in compatible, tested dependency sets.
- **Production-ready features** — health endpoints, metrics, and externalized configuration out of the box.

## Spring vs. Spring Boot at a Glance

| Concern | Plain Spring | Spring Boot |
|---|---|---|
| Server setup | Deploy WAR to external Tomcat | Embedded Tomcat started by `main()` |
| Bean configuration | `applicationContext.xml` or `@Configuration` classes | Auto-configured from classpath |
| Dependency versions | Managed manually | Managed by the BOM in `spring-boot-starter-parent` |
| Entry point | No single `main()` | `@SpringBootApplication` + `SpringApplication.run()` |
| Properties | Custom loading code | `application.properties` / `application.yml` loaded automatically |

## The `@SpringBootApplication` Annotation

Every Spring Boot app starts with one annotation that composes three others:

```java
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication   // = @Configuration + @EnableAutoConfiguration + @ComponentScan
public class DemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

- `@Configuration` — marks this class as a source of `@Bean` definitions.
- `@EnableAutoConfiguration` — tells Spring Boot to apply auto-configuration based on the classpath.
- `@ComponentScan` — scans the current package (and sub-packages) for `@Component`, `@Service`, `@Repository`, and `@Controller` classes.

## A Minimal REST Endpoint

Add `spring-boot-starter-web` to your `pom.xml` and write one class:

```xml
<!-- pom.xml (excerpt) -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.3.0</version>
</parent>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
</dependencies>
```

```java
package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello, Spring Boot!";
    }
}
```

Run the app (`mvn spring-boot:run` or the `main()` method), then call the endpoint:

```bash
curl http://localhost:8080/hello
# Hello, Spring Boot!
```

Auto-configuration detected `spring-boot-starter-web` on the classpath, started an embedded Tomcat on port 8080, and registered a `DispatcherServlet` — all without a single line of server setup code.

## How Auto-Configuration Works

Spring Boot ships hundreds of `@AutoConfiguration` classes (formerly `@Configuration` + `@Conditional`). Each fires only when its conditions are met — for example, `DataSourceAutoConfiguration` activates only when a JDBC driver JAR is present and no `DataSource` bean has been defined manually.

You can inspect which auto-configurations applied (and which were skipped) at startup:

```properties
# application.properties
logging.level.org.springframework.boot.autoconfigure=DEBUG
```

The output shows a "Positive matches" / "Negative matches" report that makes it easy to understand exactly why a bean was (or was not) created.

## The Starter Dependency System

Instead of hunting for compatible JAR versions, you add a single starter:

| Starter | What it pulls in |
|---|---|
| `spring-boot-starter-web` | Spring MVC, embedded Tomcat, Jackson JSON |
| `spring-boot-starter-data-jpa` | Hibernate, Spring Data JPA, transaction management |
| `spring-boot-starter-security` | Spring Security filter chain |
| `spring-boot-starter-test` | JUnit 5, Mockito, AssertJ, Spring test slices |
| `spring-boot-starter-validation` | Hibernate Validator (Jakarta Bean Validation) |

All version numbers are governed by the `spring-boot-starter-parent` BOM, so you almost never specify individual library versions.

## Common Mistakes to Avoid

- **Placing `main()` in the wrong package** — `@ComponentScan` scans the package of the annotated class and its sub-packages. If your controllers live in a sibling package they will not be discovered.
- **Overriding auto-configuration without understanding it** — declaring a `DataSource` bean manually disables `DataSourceAutoConfiguration`. That is intentional and powerful, but surprises developers who did not expect it.
- **Using `spring-boot-starter-parent` as a dependency instead of as a parent** — it must appear in `<parent>`, not `<dependencies>`, to activate BOM version management.
- **Ignoring the banner version** — the ASCII banner printed at startup shows the Spring Boot version. Keeping it visible helps when debugging version-related issues in logs.

## Summary

Spring Boot is Spring with sensible defaults: embedded server, auto-configured beans, curated starters, and a single `main()` entry point. It does not replace or hide the Spring Framework — it accelerates getting to the part that matters, writing business logic.
