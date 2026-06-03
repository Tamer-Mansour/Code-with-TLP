# Integration Testing with @SpringBootTest

Unit tests verify a single class in isolation. **Integration tests** verify that multiple components work together correctly — controllers, services, repositories, and the actual Spring context wired as it runs in production. In Spring Boot 3, the entry point for this is the `@SpringBootTest` annotation.

## What @SpringBootTest does

`@SpringBootTest` boots a real `ApplicationContext` for your test. It locates your `@SpringBootApplication` class, loads the bean definitions, and applies your configuration and auto-configuration. Combined with the `spring-boot-starter-test` dependency (included in every Spring Initializr project), you get JUnit 5, AssertJ, Mockito, and `MockMvc` out of the box.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

## Choosing a web environment

The `webEnvironment` attribute controls how the web layer is started:

| Value | Behavior | When to use |
|---|---|---|
| `MOCK` (default) | Mock servlet environment, no real port | Test with `MockMvc`, fastest |
| `RANDOM_PORT` | Real embedded server on a random port | End-to-end HTTP via `TestRestTemplate`/`WebTestClient` |
| `DEFINED_PORT` | Real server on the configured port | Rarely — risks port conflicts |
| `NONE` | No web environment | Non-web integration tests |

## Example: testing a REST endpoint with MockMvc

```java
@SpringBootTest
@AutoConfigureMockMvc
class GreetingControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void returnsGreetingJson() throws Exception {
        mockMvc.perform(get("/api/greeting").param("name", "Tamer"))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.message").value("Hello, Tamer"));
    }
}
```

`@AutoConfigureMockMvc` builds a fully configured `MockMvc` against the loaded context, so filters, converters, and exception handlers all participate — closer to real behavior than a standalone setup.

## Example: full HTTP with RANDOM_PORT

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class GreetingHttpTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void greetingOverRealHttp() {
        ResponseEntity<String> response =
            restTemplate.getForEntity("/api/greeting?name=TLP", String.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).contains("Hello, TLP");
    }
}
```

`TestRestTemplate` is path-relative, so you never hardcode the random port.

## Replacing collaborators with @MockBean

When you want the real context but a fake collaborator (e.g., an external payment client), use `@MockBean`. It replaces the matching bean in the context with a Mockito mock:

```java
@SpringBootTest
@AutoConfigureMockMvc
class OrderControllerTest {

    @Autowired MockMvc mockMvc;
    @MockBean PaymentGateway paymentGateway;

    @Test
    void rejectsWhenPaymentFails() throws Exception {
        when(paymentGateway.charge(anyLong())).thenReturn(false);
        mockMvc.perform(post("/api/orders").content("{...}")
                .contentType(MediaType.APPLICATION_JSON))
               .andExpect(status().isPaymentRequired());
    }
}
```

## Common mistakes and best practices

- **Use slice annotations when you don't need the whole context.** `@WebMvcTest`, `@DataJpaTest`, and `@JsonTest` load only a subset and run far faster. Reserve `@SpringBootTest` for true cross-layer tests.
- **Roll back database changes.** Add `@Transactional` to the test class so each test rolls back automatically, keeping tests independent.
- **Externalize test config.** Use `@ActiveProfiles("test")` and a `src/test/resources/application-test.yml` instead of mutating production config.
- **Prefer Testcontainers over H2** for database tests so you exercise the real engine:

```java
@SpringBootTest
@Testcontainers
class RepositoryIntegrationTest {
    @Container
    static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry r) {
        r.add("spring.datasource.url", db::getJdbcUrl);
        r.add("spring.datasource.username", db::getUsername);
        r.add("spring.datasource.password", db::getPassword);
    }
}
```

- **Don't recreate the context needlessly.** Spring caches contexts between tests with identical configuration. Mixing many distinct `@MockBean`/property combinations forces reloads and slows the suite.

**Summary:** `@SpringBootTest` loads the real Spring context for cross-layer integration testing — pick `MOCK` + `MockMvc` for speed or `RANDOM_PORT` + `TestRestTemplate` for true HTTP, mock externals with `@MockBean`, and keep tests isolated with `@Transactional` and test profiles.
