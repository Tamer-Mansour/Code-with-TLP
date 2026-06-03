# Final Quiz: Spring Boot Mastery

Test your command of the entire Spring Boot 3 / Java 17+ stack — covering IoC and DI, REST APIs, Spring Data JPA, validation, Spring Security with JWT, testing slices, production readiness, AOP, advanced transaction management, and containerisation. Each question reflects a concept or pitfall drawn from a real production codebase.

---

**Q1. A developer creates the following service but finds the dependency is `null` at runtime. What is the root cause?**

```java
@Service
public class InvoiceService {

    private final PaymentService paymentService;

    public InvoiceService() {
        // manually constructed — no Spring involvement
    }

    public void process(Long orderId) {
        paymentService.charge(orderId); // NullPointerException
    }
}
```

- [ ] `PaymentService` is not annotated with `@Service`, so Spring ignores it.
- [ ] Constructor injection requires `@Autowired` on the constructor in Spring Boot 3.
- [x] `InvoiceService` is instantiated with `new` (or via an explicit no-arg constructor that does not request `PaymentService`), so Spring never injects the field — the dependency is never populated.
- [ ] `@Service` beans must use setter injection; constructor injection is unsupported.

---

**Q2. Which HTTP method and status code combination correctly represents a successful resource creation in a RESTful Spring Boot controller?**

```java
@PostMapping("/products")
public ResponseEntity<ProductDto> create(@RequestBody @Valid ProductRequest request) {
    ProductDto created = productService.create(request);
    URI location = URI.create("/products/" + created.id());
    return ResponseEntity.created(location).body(created);
}
```

- [ ] `POST` returning `200 OK` with the created resource in the body.
- [ ] `PUT` returning `201 Created` — `POST` is for updates in REST conventions.
- [ ] `POST` returning `204 No Content` because the resource is included in the `Location` header.
- [x] `POST` returning `201 Created` with a `Location` header pointing to the new resource.

---

**Q3. You need a JPQL query that eagerly loads a `Customer` together with its `orders` collection in a single database round trip. Which repository method declaration achieves this?**

```java
@Repository
public interface CustomerRepository extends JpaRepository<Customer, Long> {

    // Option A
    Optional<Customer> findById(Long id);

    // Option B
    @Query("SELECT c FROM Customer c JOIN FETCH c.orders WHERE c.id = :id")
    Optional<Customer> findByIdWithOrders(@Param("id") Long id);
}
```

- [ ] Option A — `findById` already performs a `JOIN FETCH` automatically for all `@OneToMany` associations.
- [ ] Neither option — eager loading requires `@EntityGraph` exclusively; `JOIN FETCH` is a Hibernate-only extension not available in JPQL.
- [ ] Option A with `@Fetch(FetchMode.JOIN)` on the association; the method name alone controls the join.
- [x] Option B — the explicit `JOIN FETCH` in JPQL instructs the JPA provider to load `c.orders` in the same query, avoiding the N+1 problem.

---

**Q4. A `@ControllerAdvice` class contains the handler below. What response does a client receive when a controller throws `ProductNotFoundException` (which extends `RuntimeException`)?**

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ProductNotFoundException.class)
    public ResponseEntity<Map<String, String>> handleNotFound(ProductNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(Map.of("error", ex.getMessage()));
    }
}
```

| Field | Value |
|---|---|
| HTTP status | `404 Not Found` |
| Response body | `{"error": "<exception message>"}` |
| Content-Type | `application/json` |

- [ ] Spring rethrows the exception to the servlet container, which renders an HTML error page.
- [ ] The response is always `500 Internal Server Error` unless `@ResponseStatus` is placed on the exception class itself.
- [x] The client receives `404 Not Found` with a JSON body `{"error": "..."}` — `@ExceptionHandler` intercepts the exception before it reaches the servlet container.
- [ ] `@RestControllerAdvice` only intercepts checked exceptions; `RuntimeException` subclasses propagate normally.

---

**Q5. An aspect is written to measure the execution time of all public service methods. Which advice type and pointcut expression are correct for this purpose?**

```java
@Aspect
@Component
public class TimingAspect {

    @Around("execution(* com.example.app.service..*(..))")
    public Object time(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return pjp.proceed();
        } finally {
            long ms = System.currentTimeMillis() - start;
            System.out.println(pjp.getSignature().toShortString() + " took " + ms + " ms");
        }
    }
}
```

- [ ] `@Before` — timing must start before the method, so `@Around` is the wrong advice type.
- [ ] The pointcut expression is invalid; service packages must be listed with `within(com.example.app.service.*)` instead of `execution(...)`.
- [ ] `pjp.proceed()` must be called in a separate thread; calling it inline blocks the around advice.
- [x] The code is correct — `@Around` wraps the entire invocation, `pjp.proceed()` delegates to the real method, and the `finally` block logs the elapsed time even if an exception is thrown.

---

**Q6. Consider the following transaction setup. What happens when `auditService.recordFailure()` is called from inside `placeOrder()` and `placeOrder()` subsequently throws a `RuntimeException`?**

```java
@Service
public class OrderService {

    @Transactional
    public void placeOrder(OrderRequest request) {
        orderRepository.save(toEntity(request));
        try {
            inventoryService.reserve(request.items());
        } catch (StockException ex) {
            auditService.recordFailure(ex.getMessage()); // must survive rollback
            throw ex;
        }
    }
}

@Service
public class AuditService {

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void recordFailure(String reason) {
        auditRepository.save(new AuditEntry(reason));
    }
}
```

- [ ] `recordFailure()` is rolled back together with `placeOrder()` because they share the same `@Transactional` proxy.
- [ ] `REQUIRES_NEW` is unsupported when used with JPA; it requires a `DataSourceTransactionManager`.
- [x] `REQUIRES_NEW` suspends the outer transaction, commits the audit entry in its own independent transaction, then resumes — so the audit row persists even when `placeOrder()` rolls back.
- [ ] Spring throws `IllegalTransactionStateException` because `REQUIRES_NEW` cannot be called from within an existing transaction.

---

**Q7. A `@WebMvcTest` slice test must call a secured endpoint. The test class is shown below — what does `@WithMockUser` accomplish?**

```java
@WebMvcTest(ProductController.class)
class ProductControllerTest {

    @Autowired MockMvc mockMvc;

    @MockBean ProductService productService;

    @Test
    @WithMockUser(roles = "USER")
    void getProductById_returnsProduct() throws Exception {
        given(productService.findById(1L)).willReturn(new ProductDto(1L, "Laptop", 999.99));

        mockMvc.perform(get("/products/1"))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.name").value("Laptop"));
    }
}
```

- [ ] It starts a real `UsernamePasswordAuthenticationFilter` and authenticates against an in-memory user store.
- [ ] It disables Spring Security for the test so the endpoint is accessible without authentication.
- [x] It populates the `SecurityContext` with a mock `Authentication` carrying the specified roles, allowing the request to pass security checks without involving `UserDetailsService` or JWT.
- [ ] It injects a `@MockBean` for `UserDetailsService` and stubs `loadUserByUsername` to return the mock user.

---

**Q8. Which `application.properties` property exposes ALL Spring Boot Actuator endpoints over HTTP, and what additional configuration is strongly recommended in production?**

```properties
# Expose all endpoints
management.endpoints.web.exposure.include=*
```

- [ ] No additional configuration is needed — Actuator endpoints only expose read-only information and carry no security risk.
- [ ] Set `management.endpoint.health.enabled=false` to disable health checks before exposing the rest.
- [ ] Actuator requires `spring-boot-starter-security` to expose any endpoint; the `include=*` setting is ignored without it.
- [x] Running the management server on a dedicated port (`management.server.port=8081`) and protecting it at the network/firewall level is strongly recommended, because endpoints like `/env` and `/heapdump` can expose secrets and heap contents.

---

**Q9. A multi-stage `Dockerfile` for a Spring Boot 3 app is shown below. Which line is the most important for keeping Docker's layer cache effective across source-code-only changes?**

```dockerfile
FROM eclipse-temurin:17-jdk AS build        # line 1
WORKDIR /app                                # line 2
COPY .mvn/ .mvn/                            # line 3
COPY mvnw pom.xml ./                        # line 4
RUN ./mvnw dependency:go-offline -B         # line 5
COPY src ./src                              # line 6
RUN ./mvnw clean package -DskipTests -B     # line 7

FROM eclipse-temurin:17-jre AS runtime      # line 8
WORKDIR /app                                # line 9
RUN useradd -r -u 1001 appuser             # line 10
USER appuser                                # line 11
COPY --from=build /app/target/*.jar app.jar # line 12
EXPOSE 8080                                 # line 13
ENTRYPOINT ["java", "-jar", "/app/app.jar"] # line 14
```

- [ ] Line 1 — using `eclipse-temurin:17-jdk` rather than `latest` pins the Java version and avoids cache misses.
- [ ] Line 7 — skipping tests with `-DskipTests` speeds up the build and keeps the layer stable.
- [ ] Line 8 — switching to a JRE in the runtime stage avoids including unused JDK tooling.
- [x] Lines 3–5 — copying only `pom.xml` (and the Maven wrapper) and resolving dependencies before copying `src` means the dependency-download layer is invalidated only when `pom.xml` changes, not on every source edit.

---

**Q10. The following integration test uses `@SpringBootTest` with a real application context. What is the role of `@ActiveProfiles("test")` and the `application-test.properties` file it activates?**

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
class OrderApiIntegrationTest {

    @Autowired TestRestTemplate restTemplate;

    @Test
    void createOrder_returns201() {
        OrderRequest body = new OrderRequest(1L, List.of(new Item("SKU-1", 2)));
        ResponseEntity<OrderDto> resp = restTemplate.postForEntity("/orders", body, OrderDto.class);
        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.CREATED);
    }
}
```

```properties
# src/test/resources/application-test.properties
spring.datasource.url=jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true
```

- [ ] `@ActiveProfiles("test")` disables all beans annotated with `@Profile("prod")` but has no effect on `application.properties` values.
- [ ] It causes Spring Boot to skip auto-configuration for the data source and use `@DataJpaTest` behaviour instead.
- [ ] The `application-test.properties` file must be placed in `src/main/resources` to be resolved by the test context.
- [x] `@ActiveProfiles("test")` tells Spring Boot to merge `application-test.properties` into the environment, overriding the production data-source URL with an in-memory H2 database and configuring `create-drop` DDL — isolating tests from any external database.
