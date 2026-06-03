# The Testing Pyramid and JUnit 5

Automated testing is a first-class concern in Spring Boot projects. Before writing a single test method, it helps to understand *where* that test sits in the overall quality strategy — and that is exactly what the Testing Pyramid communicates.

## The Testing Pyramid

The pyramid describes three layers of automated tests, ordered from fastest-and-cheapest at the base to slowest-and-costliest at the top:

| Layer | Scope | Speed | Typical Ratio |
|---|---|---|---|
| **Unit tests** | One class in isolation, dependencies mocked | Milliseconds | ~70 % |
| **Integration tests** | Multiple components wired together (Spring context, DB) | Seconds | ~20 % |
| **End-to-end (E2E) tests** | Full running application, real HTTP, real database | Minutes | ~10 % |

The recommendation is to invest most effort at the base. Unit tests are deterministic, give instant feedback, and require no infrastructure. Integration and E2E tests catch wiring and contract issues that unit tests cannot, but they cost more to run and maintain.

## JUnit 5 in Spring Boot 3

Spring Boot 3's `spring-boot-starter-test` dependency pulls in JUnit 5 (Jupiter) automatically — no extra configuration needed.

```xml
<!-- pom.xml — already included by the starter -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

The starter also brings Mockito, AssertJ, and Hamcrest, covering every layer of the pyramid out of the box.

## Writing a Unit Test with JUnit 5

Consider a simple service that calculates a discounted price:

```java
// src/main/java/com/example/catalog/PricingService.java
@Service
public class PricingService {

    public double applyDiscount(double price, double discountPercent) {
        if (discountPercent < 0 || discountPercent > 100) {
            throw new IllegalArgumentException("Discount must be between 0 and 100");
        }
        return price - (price * discountPercent / 100);
    }
}
```

The unit test verifies the logic without starting a Spring context:

```java
// src/test/java/com/example/catalog/PricingServiceTest.java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.assertj.core.api.Assertions.*;

class PricingServiceTest {

    private final PricingService pricingService = new PricingService();

    @Test
    @DisplayName("should apply a 20 % discount correctly")
    void applyDiscount_validPercent_returnsDiscountedPrice() {
        double result = pricingService.applyDiscount(100.0, 20.0);
        assertThat(result).isEqualTo(80.0);
    }

    @Test
    @DisplayName("should throw when discount is negative")
    void applyDiscount_negativePercent_throwsException() {
        assertThatThrownBy(() -> pricingService.applyDiscount(100.0, -5.0))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("between 0 and 100");
    }
}
```

Key JUnit 5 annotations used here:

- `@Test` — marks a method as a test case.
- `@DisplayName` — provides a human-readable label shown in IDE and CI reports.
- AssertJ's `assertThat` and `assertThatThrownBy` — fluent, readable assertions preferred over JUnit's built-in `assertEquals`.

## Key JUnit 5 Annotations at a Glance

```java
@BeforeEach   // runs before every @Test method — set up shared state
@AfterEach    // runs after every @Test method — tear down / reset
@BeforeAll    // runs once before all tests in the class (must be static)
@AfterAll     // runs once after  all tests in the class (must be static)
@Disabled     // skips a test with an optional reason string
@ParameterizedTest // runs the same test with multiple inputs
```

## Common Mistakes and Best Practices

- **Do not use `@SpringBootTest` for pure logic.** Loading the full application context adds several seconds per run. Reserve it for integration tests.
- **Name tests descriptively.** Use the pattern `methodName_condition_expectedBehavior` so failures self-document.
- **One assertion focus per test.** Tests that check many unrelated things are hard to diagnose when they fail.
- **Avoid `static` mutable state** shared across tests. Use `@BeforeEach` to reinitialize state cleanly.
- **Use AssertJ** over raw JUnit assertions — the error messages are far more informative (e.g., `expected: 80.0 but was: 75.0`).

## Summary

The Testing Pyramid guides you to write many fast unit tests and fewer expensive integration/E2E tests. JUnit 5, bundled with `spring-boot-starter-test`, provides the annotations and lifecycle hooks needed to structure those unit tests cleanly and readably.
