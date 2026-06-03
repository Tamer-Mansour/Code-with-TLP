# Quiz: Testing Spring Apps

Test your understanding of unit testing with JUnit 5 and Mockito, slice tests (`@WebMvcTest`, `@DataJpaTest`), full-context integration tests with `@SpringBootTest`, `MockMvc`, `TestRestTemplate`, Testcontainers, and Spring Security test support.

---

**Q1. Which annotation loads the full Spring application context and starts an embedded server on a random port, making it suitable for end-to-end integration tests?**
- [ ] `@WebMvcTest`
- [ ] `@DataJpaTest`
- [ ] `@ContextConfiguration`
- [x] `@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)`

> `@SpringBootTest` bootstraps the complete `ApplicationContext`. Setting `webEnvironment = RANDOM_PORT` starts a real embedded servlet container on a random free port, which you can inject with `@LocalServerPort`. `@WebMvcTest` and `@DataJpaTest` are slice tests that load only a subset of the context.

---

**Q2. You are writing a unit test for a `ProductService` that depends on `ProductRepository`. Which is the correct way to inject a Mockito mock of the repository into the service under test?**

```java
@ExtendWith(MockitoExtension.class)
class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    @InjectMocks
    private ProductService productService;

    @Test
    void findById_returnsProduct_whenExists() {
        var product = new Product(1L, "Laptop", 999.0);
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));

        Product result = productService.findById(1L);

        assertThat(result.getName()).isEqualTo("Laptop");
        verify(productRepository).findById(1L);
    }
}
```

- [x] `@ExtendWith(MockitoExtension.class)` with `@Mock` and `@InjectMocks` — no Spring context needed.
- [ ] `@SpringBootTest` with `@MockBean` — `@InjectMocks` does not work without a Spring context.
- [ ] `@WebMvcTest` with `@Autowired` — service beans are automatically mocked by the slice.
- [ ] `Mockito.mock(ProductRepository.class)` must be called inside `@BeforeAll`; field annotations are not supported in JUnit 5.

> `MockitoExtension` activates Mockito annotations without starting any Spring context, making the test fast and isolated. `@InjectMocks` creates the class under test and injects all `@Mock` fields into it via constructor, setter, or field injection.

---

**Q3. `@WebMvcTest(ProductController.class)` loads which parts of the application context?**
- [ ] The full context including all `@Service`, `@Repository`, and `@Component` beans.
- [ ] Only JPA repositories and the `DataSource`.
- [x] Only the web layer — controllers, `@ControllerAdvice`, filters, `WebMvcConfigurer`, and related beans — while all `@Service` and `@Repository` beans must be provided as `@MockBean`.
- [ ] Nothing by default; you must list every bean class in the `classes` attribute.

> `@WebMvcTest` is a slice annotation that auto-configures `MockMvc` and restricts the context to the web layer. Any downstream dependency (e.g., a `ProductService`) must be declared with `@MockBean` so Mockito provides a stand-in, keeping the test fast and focused.

---

**Q4. What does the following `MockMvc` test verify?**

```java
@WebMvcTest(ProductController.class)
class ProductControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ProductService productService;

    @Test
    void getProduct_returns404_whenNotFound() throws Exception {
        when(productService.findById(99L)).thenThrow(new ProductNotFoundException(99L));

        mockMvc.perform(get("/products/99"))
               .andExpect(status().isNotFound())
               .andExpect(jsonPath("$.status").value(404));
    }
}
```

- [ ] It starts a real HTTP server and sends an actual TCP request to `/products/99`.
- [ ] It verifies that `ProductRepository.findById(99L)` returns an empty `Optional`.
- [ ] It only checks the URL mapping; response body assertions require `TestRestTemplate`.
- [x] It performs a mock HTTP GET request entirely in-memory and asserts that the controller returns a 404 status with a JSON body containing `"status": 404`.

> `MockMvc` dispatches requests through the full Spring MVC pipeline (handler mapping, interceptors, argument resolvers, message converters, exception handlers) without starting a TCP server. `jsonPath` evaluates JSONPath expressions against the response body using the Jayway library included with `spring-boot-starter-test`.

---

**Q5. Which annotation replaces a real Spring bean in the `ApplicationContext` with a Mockito mock during a `@SpringBootTest` integration test?**
- [ ] `@Mock`
- [ ] `@InjectMocks`
- [ ] `@Spy`
- [x] `@MockBean`

> `@MockBean` (from `spring-boot-test`) creates a Mockito mock and registers it as a bean in the Spring context, replacing any existing bean of the same type. `@Mock` is a pure-Mockito annotation that has no awareness of the Spring context and cannot replace a Spring-managed bean.

---

**Q6. `@DataJpaTest` auto-configures an in-memory H2 database by default. Which property would you add to `@DataJpaTest` to run the slice against your actual configured `DataSource` (e.g., a PostgreSQL Testcontainer) instead?**

```java
@DataJpaTest(???)
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class OrderRepositoryTest { ... }
```

| `replace` value | Effect |
|---|---|
| `Replace.ANY` (default) | Always replace the datasource with an embedded one |
| `Replace.AUTO_CONFIGURED` | Replace only if the datasource was auto-configured |
| `Replace.NONE` | Keep the datasource from the application context as-is |

- [x] `@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)` — prevents the slice from substituting the real datasource with H2.
- [ ] `@DataJpaTest(useDefaultFilters = false)` — disabling default filters exposes the real datasource.
- [ ] `spring.datasource.url=jdbc:h2:mem:testdb` in `application-test.properties` — a test profile overrides the slice.
- [ ] No change is needed; `@DataJpaTest` always uses the configured datasource.

---

**Q7. You want to test your Spring Security configuration and assert that an unauthenticated `GET /admin/users` request returns HTTP 401. Which test setup is correct?**

```java
@WebMvcTest(AdminController.class)
class AdminControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    void adminEndpoint_returns401_whenUnauthenticated() throws Exception {
        mockMvc.perform(get("/admin/users"))
               .andExpect(status().isUnauthorized());
    }
}
```

- [ ] `@WebMvcTest` never loads the `SecurityFilterChain`; this test always gets 200.
- [ ] You must use `@SpringBootTest(webEnvironment = RANDOM_PORT)` to activate security filters.
- [ ] Add `@WithMockUser` to the test method — without it, `MockMvc` cannot invoke the endpoint at all.
- [x] The setup is correct — `@WebMvcTest` includes `SecurityAutoConfiguration`, so the security filter chain is active and an unauthenticated request to a secured endpoint returns 401.

> `@WebMvcTest` auto-configures Spring Security by default. To simulate an authenticated user, annotate the test method with `@WithMockUser` (for basic role-based checks) or build a custom `SecurityMockMvcRequestPostProcessor` via `SecurityMockMvcRequestBuilders`.

---

**Q8. Which Testcontainers annotation, combined with the JUnit 5 extension, automatically starts a Docker container once for all tests in a class and stops it when the class finishes?**

```java
@SpringBootTest
@Testcontainers
class PaymentServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres =
            new PostgreSQLContainer<>("postgres:16-alpine")
                .withDatabaseName("payments_test")
                .withUsername("test")
                .withPassword("test");

    @DynamicPropertySource
    static void configureDataSource(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
}
```

- [ ] `@Container` on a non-static field starts a new container per test method, not per class.
- [ ] `@Testcontainers` is not required; Testcontainers starts automatically when the field is declared.
- [ ] `@DynamicPropertySource` is only supported with `@DataJpaTest`, not `@SpringBootTest`.
- [x] `@Container` on a `static` field combined with `@Testcontainers` on the class starts the container once for all tests in the class; `@DynamicPropertySource` wires the container's JDBC URL into the Spring context before it is created.

> Using a `static` field is the key: a non-static `@Container` restarts on every test method. `@DynamicPropertySource` runs before `@SpringBootTest` refreshes the context, ensuring the datasource URL points to the running container.

---

**Q9. What is the purpose of `@Transactional` on a `@DataJpaTest` test method, and what happens to the database state after the test completes?**
- [ ] It ensures the test acquires a pessimistic lock on all queried rows.
- [ ] It promotes the test to use a real database transaction instead of an in-memory mock.
- [ ] It has no effect in tests; `@Transactional` is only meaningful in production `@Service` beans.
- [x] Each test method runs inside a transaction that is automatically rolled back after the test completes, leaving the database in a clean state for the next test.

> `@DataJpaTest` applies `@Transactional` at the class level by default. Rollback on completion means tests are isolated without any `@BeforeEach` cleanup queries. If you need to verify committed state (e.g., test a method that spawns a new transaction with `REQUIRES_NEW`), annotate the test with `@Commit` to override the default rollback.

---

**Q10. Given the following service and test, which assertion library method correctly verifies that calling `productService.findById(0L)` throws a `ProductNotFoundException`?**

```java
// Service
public Product findById(Long id) {
    return productRepository.findById(id)
            .orElseThrow(() -> new ProductNotFoundException(id));
}

// Test (JUnit 5 + AssertJ)
@Test
void findById_throwsException_whenProductMissing() {
    when(productRepository.findById(0L)).thenReturn(Optional.empty());

    // Which assertion goes here?
}
```

- [ ] `assertTrue(productService.findById(0L) == null);`
- [ ] `assertNull(productService.findById(0L));`
- [x] `assertThatThrownBy(() -> productService.findById(0L)).isInstanceOf(ProductNotFoundException.class);`
- [ ] `Mockito.verify(productRepository).orElseThrow();`

> AssertJ's `assertThatThrownBy` captures the exception thrown by the lambda and chains fluent assertions on it. The equivalent JUnit 5 API is `assertThrows(ProductNotFoundException.class, () -> productService.findById(0L))`. Both are idiomatic; AssertJ is preferred when you need to assert on the exception's message or cause.
