# Quiz: Advanced Spring

Test your understanding of Aspect-Oriented Programming, Spring Cache abstraction, async method execution, scheduled tasks, and transaction propagation and isolation — the topics that separate a competent Spring developer from an advanced one.

---

**Q1. Which annotation must be placed on a Spring `@Configuration` class (or the main application class) to activate the Spring AOP proxy infrastructure for `@Aspect` beans?**

```java
@Configuration
@/* which annotation? */
public class AopConfig { }
```

- [ ] `@EnableAspectJWeaving`
- [ ] `@EnableProxySupport`
- [x] `@EnableAspectJAutoProxy`
- [ ] `@EnableAOP`

---

**Q2. Examine the pointcut expression below. Which join points does it match?**

```java
@Around("execution(* com.example.service.*Service.*(..))")
public Object logExecution(ProceedingJoinPoint pjp) throws Throwable {
    // ...
}
```

- [ ] Every public method in any class under `com.example.service`, regardless of the class name.
- [ ] Only methods on Spring beans whose interface names end in `Service`.
- [x] Every method with any return type on any class whose name ends in `Service` inside the `com.example.service` package.
- [ ] Only `void` methods on classes annotated with `@Service` in the `com.example.service` package.

---

**Q3. What is the correct order in which AOP advice types execute around a successfully completing method?**

| Advice type | Runs |
|---|---|
| `@Before` | Before the method |
| `@AfterReturning` | After a successful return |
| `@AfterThrowing` | After an exception |
| `@After` | Always after (finally) |
| `@Around` | Before and after (wraps the call) |

- [ ] `@Around` (before) → `@After` → `@Before` → method → `@AfterReturning`
- [ ] `@Before` → method → `@AfterThrowing` → `@After` → `@Around` (after)
- [ ] `@Before` → method → `@AfterReturning` → `@Around` (after) → `@After`
- [x] `@Around` (before) → `@Before` → method → `@AfterReturning` → `@After` → `@Around` (after)

---

**Q4. Which two annotations are required to enable the Spring Cache abstraction in a Spring Boot 3 application and to mark a method whose return value should be stored in the cache?**

```java
// On the @SpringBootApplication or a @Configuration class:
@/* annotation A */

// On the service method:
@/* annotation B */(value = "products", key = "#id")
public Product findById(Long id) { ... }
```

- [ ] `@EnableCaching` / `@CacheEvict`
- [ ] `@EnableCache` / `@Cached`
- [x] `@EnableCaching` / `@Cacheable`
- [ ] `@CacheConfig` / `@CachePut`

---

**Q5. A developer writes the following caching code. What is the difference in behaviour between `@Cacheable` and `@CachePut` on these two methods?**

```java
@Cacheable(value = "users", key = "#id")
public User getUser(Long id) {
    return userRepository.findById(id).orElseThrow();
}

@CachePut(value = "users", key = "#user.id")
public User updateUser(User user) {
    return userRepository.save(user);
}
```

- [ ] Both annotations always execute the method body and store the result — they are interchangeable.
- [x] `@Cacheable` skips the method body on a cache hit (returns cached value); `@CachePut` always executes the method body and updates the cache with the new result.
- [ ] `@Cacheable` writes to the cache; `@CachePut` reads from the cache.
- [ ] `@CachePut` evicts the cache entry before execution; `@Cacheable` evicts it after.

---

**Q6. Which annotation enables support for `@Async` methods in Spring, and what is the key behavioural requirement for `@Async` to work correctly?**

```java
@Configuration
@EnableAsync
public class AsyncConfig { }

@Service
public class ReportService {

    @Async
    public CompletableFuture<Report> generateReport(Long userId) {
        // long-running work
        return CompletableFuture.completedFuture(report);
    }
}
```

- [ ] `@EnableAsync` is not needed — `@Async` is activated automatically by `spring-boot-autoconfigure`.
- [ ] `@Async` works on private methods as long as the class is annotated with `@Service`.
- [ ] The return type must always be `void`; `CompletableFuture` is not supported.
- [x] `@EnableAsync` activates the async proxy; `@Async` must be on a public method called from *outside* the bean (self-invocation bypasses the proxy and runs synchronously).

---

**Q7. What does the following `@Scheduled` method do, and what annotation on a configuration class is required to activate it?**

```java
@Scheduled(cron = "0 0 2 * * *")
public void archiveOldOrders() {
    orderService.archiveOrdersBefore(LocalDate.now().minusDays(90));
}
```

- [ ] It runs `archiveOldOrders` every 2 minutes, every day; requires `@EnableScheduling`.
- [ ] It runs `archiveOldOrders` every 2 seconds; no extra annotation is needed.
- [x] It runs `archiveOldOrders` every day at 02:00 (midnight + 2 hours); requires `@EnableScheduling` on a configuration class.
- [ ] It runs `archiveOldOrders` on the second day of every month at midnight; requires `@EnableScheduling`.

---

**Q8. Consider the following service and its caller. Which transaction propagation behaviour correctly describes what happens when `inner()` is called from `outer()`?**

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void inner() {
    // DB write B
}

@Transactional
public void outer() {
    // DB write A
    inner();
    // DB write C
}
```

- [ ] `inner()` joins the transaction started by `outer()` — both writes share one transaction.
- [ ] `inner()` throws `IllegalTransactionStateException` because a transaction is already active.
- [ ] Both transactions commit together when `outer()` returns.
- [x] `inner()` suspends the transaction from `outer()`, starts a brand-new independent transaction, and commits (or rolls back) that transaction before resuming `outer()`'s transaction.

---

**Q9. A banking service transfers funds between two accounts. Which isolation level prevents "dirty reads" (reading uncommitted data from another transaction) but still allows "non-repeatable reads"?**

| Isolation level | Dirty read | Non-repeatable read | Phantom read |
|---|---|---|---|
| `READ_UNCOMMITTED` | possible | possible | possible |
| `READ_COMMITTED` | prevented | possible | possible |
| `REPEATABLE_READ` | prevented | prevented | possible |
| `SERIALIZABLE` | prevented | prevented | prevented |

- [ ] `Isolation.READ_UNCOMMITTED`
- [x] `Isolation.READ_COMMITTED`
- [ ] `Isolation.REPEATABLE_READ`
- [ ] `Isolation.SERIALIZABLE`

---

**Q10. A developer adds the following aspect but discovers it never fires in tests. What is the most likely cause?**

```java
@Aspect
@Component
public class AuditAspect {

    @Before("execution(* com.example.service.OrderService.placeOrder(..))")
    public void auditOrder(JoinPoint jp) {
        log.info("Placing order: {}", jp.getArgs());
    }
}
```

```java
@Service
public class OrderService {

    public void processAll(List<Order> orders) {
        for (Order o : orders) {
            placeOrder(o);   // called internally
        }
    }

    public void placeOrder(Order order) { ... }
}
```

- [ ] The pointcut expression syntax is wrong — `execution` requires a fully qualified return type.
- [ ] `@Component` is missing from the aspect class.
- [ ] `@EnableAspectJAutoProxy` must be declared on the aspect class itself.
- [x] `placeOrder` is called via `this` (self-invocation) inside the same bean, so the Spring proxy is bypassed and the advice never executes.
