# Quiz: Spring Core & DI

Test your understanding of Inversion of Control, the Spring Application Context, bean lifecycle, component scanning, stereotype annotations, Java-based configuration, and dependency injection styles.

---

**Q1. What does "Inversion of Control" mean in the context of the Spring Framework?**
- [ ] The application controls which version of Spring is loaded at runtime.
- [ ] Spring inverts the order of method calls inside a class to improve performance.
- [x] Object creation and dependency wiring are delegated to the Spring container rather than being managed by the application code itself.
- [ ] Controller classes are responsible for creating Service and Repository beans.

---

**Q2. Which annotation tells Spring to automatically discover and register a class as a bean during component scanning?**
- [ ] `@Bean`
- [ ] `@Inject`
- [ ] `@Autowired`
- [x] `@Component`

> `@Component` (and its specialisations `@Service`, `@Repository`, `@Controller`) marks a class for classpath scanning. `@Bean` is used inside `@Configuration` classes to declare a bean explicitly.

---

**Q3. Given the following code, what injection style is being used?**

```java
@Service
public class OrderService {

    private final PaymentGateway paymentGateway;

    public OrderService(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }
}
```

- [ ] Field injection
- [ ] Setter injection
- [x] Constructor injection
- [ ] Interface injection

> Constructor injection is the recommended style in Spring because it makes dependencies explicit, supports immutability (`final` fields), and simplifies unit testing without the Spring context.

---

**Q4. You have two beans that implement the same interface and Spring cannot determine which one to autowire. Which annotation resolves this ambiguity by name?**
- [ ] `@Primary`
- [x] `@Qualifier`
- [ ] `@Profile`
- [ ] `@Scope`

> `@Qualifier("beanName")` narrows the candidate to a specific bean. `@Primary` marks one candidate as the default when no qualifier is given, but `@Qualifier` takes precedence when both are present.

---

**Q5. What is the default bean scope in a Spring application context?**

| Scope | Description |
|---|---|
| `singleton` | One shared instance per application context |
| `prototype` | New instance created every time the bean is requested |
| `request` | New instance per HTTP request (web contexts only) |
| `session` | New instance per HTTP session (web contexts only) |

- [ ] `prototype`
- [ ] `request`
- [x] `singleton`
- [ ] `session`

---

**Q6. Which annotation is used on a `@Configuration` class method to explicitly declare a Spring bean?**
- [ ] `@Component`
- [ ] `@Autowired`
- [x] `@Bean`
- [ ] `@Service`

```java
@Configuration
public class AppConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

> Methods annotated with `@Bean` inside a `@Configuration` class are intercepted by Spring's CGLIB proxy so that calling `passwordEncoder()` directly always returns the same singleton instance.

---

**Q7. What happens when you annotate a field with `@Autowired` and Spring finds no matching bean in the context?**
- [ ] Spring silently injects `null` and continues startup.
- [ ] Spring creates a default no-arg instance of the required type.
- [ ] The application starts but logs a warning at the WARN level.
- [x] Spring throws a `NoSuchBeanDefinitionException` and the application fails to start.

> By default, `@Autowired` is `required = true`. You must explicitly set `@Autowired(required = false)` if the dependency is optional, in which case Spring injects `null` when no bean is found.

---

**Q8. Which stereotype annotation should you prefer for a class that directly interacts with the database layer? It also enables Spring's persistence exception translation.**
- [ ] `@Component`
- [ ] `@Service`
- [ ] `@Controller`
- [x] `@Repository`

> `@Repository` is semantically equivalent to `@Component` for scanning purposes, but it additionally enables a `PersistenceExceptionTranslationPostProcessor` that converts vendor-specific exceptions (e.g., Hibernate's `ConstraintViolationException`) into Spring's unified `DataAccessException` hierarchy.

---

**Q9. Consider this configuration. Under which condition will Spring activate the `DevDataSourceConfig` bean?**

```java
@Configuration
@Profile("dev")
public class DevDataSourceConfig {

    @Bean
    public DataSource dataSource() {
        return new EmbeddedDatabaseBuilder()
                .setType(EmbeddedDatabaseType.H2)
                .build();
    }
}
```

- [ ] Whenever the application is compiled with the `dev` Maven profile.
- [x] When the active Spring profile is set to `dev` (e.g., via `spring.profiles.active=dev`).
- [ ] When the class is placed in a package named `dev`.
- [ ] When the `dev` system property is present, regardless of the Spring profile.

---

**Q10. Which of the following is a correct way to inject a property value from `application.properties` into a Spring-managed bean?**
- [ ] `@Inject("${app.title}")`
- [ ] `@Autowired("${app.title}")`
- [ ] `@Config("app.title")`
- [x] `@Value("${app.title}")`

```java
// application.properties
app.title=Spring Boot Mastery

// Bean
@Component
public class AppInfo {

    @Value("${app.title}")
    private String title;
}
```

> `@Value` resolves property placeholders (`${...}`) and Spring Expression Language expressions (`#{...}`) at injection time. If the property key is missing and no default is provided (e.g., `${app.title:Default}`), Spring throws an `IllegalArgumentException` on startup.
