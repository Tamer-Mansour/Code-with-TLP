# Exercise: Dependency Injection Container Simulator

Spring's IoC container builds beans in the correct order by resolving dependencies transitively. Before instantiating `OrderService`, it must first instantiate `OrderRepository` and `EmailService` — the beans that `OrderService` depends on. This process is essentially a **topological sort** of the dependency graph.

## What you need to implement

Simulate a minimal DI container that:

1. Accepts a set of bean definitions, each listing a bean's dependencies.
2. Resolves the full dependency chain for a requested bean.
3. Prints the instantiation order — deepest dependencies first, requested bean last.
4. Detects circular dependencies and reports them.

## Real-world connection

When Spring Boot starts, `ApplicationContext.refresh()` performs exactly this traversal. It detects `@Autowired` or constructor-parameter types, walks the dependency graph, and throws `BeanCurrentlyInCreationException` when a cycle is detected (equivalent to your `CIRCULAR DEPENDENCY` output).

Circular dependencies are a design smell — they usually mean two services are doing each other's jobs and should be refactored. Spring can resolve circular dependencies through setter injection, but constructor injection (the recommended style) forces the cycle to be broken.

## Input format

```
N
BeanName1 ClassName1 dep1 dep2 ...
BeanName2 ClassName2
...
targetBeanName
```

- First line: `N` — the number of bean definitions.
- Next `N` lines: `BeanName ClassName dep1 dep2 ...` where `dep1 dep2 ...` are optional dependency bean names.
- Last line: the bean name to resolve.

## Output format

Print the class name of each bean in the order it must be instantiated, one per line. If a circular dependency exists anywhere in the resolution chain, print `CIRCULAR DEPENDENCY` instead.

## Example

**Input:**
```
4
orderService OrderService orderRepository emailService
orderRepository JdbcOrderRepository
emailService SmtpEmailService
auditService AuditService orderService
orderService
```

**Output:**
```
JdbcOrderRepository
SmtpEmailService
OrderService
```

`JdbcOrderRepository` and `SmtpEmailService` have no dependencies and are instantiated first. `OrderService` depends on both and is created last.

## Further reading

- [Spring Boot Reference — Bean Dependencies](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [Spring Boot Community eBook](https://riptutorial.com/ebook/spring-boot) — Chapter on IoC and the ApplicationContext
