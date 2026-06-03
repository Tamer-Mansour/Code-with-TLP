# Inversion of Control and Dependency Injection

At the heart of Spring lies a single, powerful idea: **Inversion of Control (IoC)**. Instead of your objects creating and wiring their own collaborators, you hand that responsibility over to a container. The container builds your objects, supplies their dependencies, and manages their lifecycle. **Dependency Injection (DI)** is the concrete technique Spring uses to achieve IoC.

## The problem DI solves

Consider a service that depends on a repository. Without DI, the service constructs its own dependency:

```java
public class OrderService {
    private final OrderRepository repository = new JdbcOrderRepository(); // tight coupling
}
```

This is rigid: `OrderService` is welded to one implementation, you cannot swap it for a test double, and you cannot reconfigure it without editing source code. **Control** of the dependency lives inside the class.

With IoC, control is *inverted* — the dependency is provided from the outside:

```java
import org.springframework.stereotype.Service;

@Service
public class OrderService {

    private final OrderRepository repository;

    // Spring injects the dependency through the constructor
    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }

    public void place(Order order) {
        repository.save(order);
    }
}
```

`OrderService` now declares *what* it needs and lets the Spring `ApplicationContext` decide *how* to satisfy it.

## How Spring wires beans

Objects managed by the container are called **beans**. You register them with stereotype annotations such as `@Component`, `@Service`, `@Repository`, or `@Configuration`, and Spring discovers them via component scanning:

```java
import org.springframework.stereotype.Repository;

@Repository
public class JdbcOrderRepository implements OrderRepository {
    @Override
    public void save(Order order) { /* JDBC logic */ }
}
```

When Spring Boot starts, it sees `OrderService` needs an `OrderRepository`, finds `JdbcOrderRepository`, and injects it automatically. No `new`, no factories, no manual wiring.

## Types of injection

| Type | How it looks | When to use |
|------|--------------|-------------|
| **Constructor** | dependency passed into the constructor | Preferred. Enables `final` fields, guarantees a fully initialized object, easy to test |
| **Setter** | `@Autowired` on a setter method | Optional or reconfigurable dependencies |
| **Field** | `@Autowired` directly on a field | Discouraged — hides dependencies and breaks unit testing |

Spring recommends **constructor injection**. Since Spring 4.3, if a class has a single constructor, `@Autowired` is optional — making the example above completely annotation-free on the constructor.

## A quick configuration alternative

Beyond stereotype annotations, you can declare beans explicitly with `@Bean` methods. This is essential for third-party classes you cannot annotate:

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {

    @Bean
    public OrderRepository orderRepository() {
        return new JdbcOrderRepository();
    }
}
```

## Common mistakes and best practices

- **Avoid field injection.** It makes dependencies invisible and forces reflection in tests. Prefer constructor injection.
- **Make injected fields `final`.** Constructor injection lets you do this, catching missing dependencies at compile time.
- **Don't fight the container.** Calling `new OrderService(...)` yourself skips proxying for transactions, caching, and AOP.
- **Resolve ambiguity explicitly.** If two beans match one type, Spring throws `NoUniqueBeanDefinitionException`. Use `@Primary` or `@Qualifier("name")` to choose.
- **Program to interfaces.** Inject `OrderRepository`, not `JdbcOrderRepository`, so implementations stay swappable.

```java
public OrderService(@Qualifier("jdbcOrderRepository") OrderRepository repository) {
    this.repository = repository;
}
```

## Summary

IoC hands object creation and wiring to the Spring container; Dependency Injection is how that wiring happens. Favor constructor injection with `final` fields and interface-typed dependencies for code that is loosely coupled, testable, and easy to reconfigure.
