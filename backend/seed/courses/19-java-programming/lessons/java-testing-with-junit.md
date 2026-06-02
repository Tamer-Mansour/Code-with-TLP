# Unit Testing with JUnit 5

JUnit 5 (also called JUnit Jupiter) is the standard testing framework for Java. Combining it with **Mockito** covers the vast majority of unit testing needs.

## Adding JUnit 5 (Maven)

```xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.2</version>
    <scope>test</scope>
</dependency>
```

With Gradle (Kotlin DSL):

```kotlin
testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
testRuntimeOnly("org.junit.platform:junit-platform-launcher")
```

## Writing a test class

```java
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {

    private Calculator calc;

    @BeforeEach
    void setUp() {
        calc = new Calculator();
    }

    @Test
    void addition_returnsCorrectSum() {
        assertEquals(5, calc.add(2, 3));
    }

    @Test
    void division_byZero_throwsException() {
        assertThrows(IllegalArgumentException.class, () -> calc.divide(10, 0));
    }

    @Test
    @DisplayName("Subtraction handles negative results")
    void subtraction_negativeResult() {
        assertTrue(calc.subtract(3, 5) < 0);
    }
}
```

## Assertions

```java
assertEquals(expected, actual);
assertNotEquals(a, b);
assertTrue(condition);
assertFalse(condition);
assertNull(obj);
assertNotNull(obj);
assertThrows(ExType.class, () -> code());
assertDoesNotThrow(() -> code());
assertAll(                              // group assertions — all run even if some fail
    () -> assertEquals(1, x),
    () -> assertTrue(y > 0)
);
```

## Lifecycle annotations

| Annotation | Runs |
|-----------|------|
| `@BeforeAll` | Once before all tests in the class (must be `static`) |
| `@BeforeEach` | Before each test method |
| `@AfterEach` | After each test method |
| `@AfterAll` | Once after all tests (`static`) |

## Parameterized tests

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.*;

@ParameterizedTest
@ValueSource(ints = {1, 2, 3, 4, 5})
void isPositive(int n) {
    assertTrue(n > 0);
}

@ParameterizedTest
@CsvSource({
    "2, 3, 5",
    "0, 0, 0",
    "-1, 1, 0"
})
void add(int a, int b, int expected) {
    assertEquals(expected, new Calculator().add(a, b));
}
```

## Mocking with Mockito

```java
import org.mockito.*;
import static org.mockito.Mockito.*;

class UserServiceTest {
    @Mock
    private UserRepository repo;

    @InjectMocks
    private UserService service;

    @BeforeEach
    void init() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void findUser_returnsUser_whenExists() {
        User alice = new User(1L, "Alice");
        when(repo.findById(1L)).thenReturn(Optional.of(alice));

        User result = service.findUser(1L);

        assertEquals("Alice", result.name());
        verify(repo, times(1)).findById(1L);
    }

    @Test
    void findUser_throwsException_whenNotFound() {
        when(repo.findById(99L)).thenReturn(Optional.empty());
        assertThrows(UserNotFoundException.class, () -> service.findUser(99L));
    }
}
```

## Test naming conventions

Good test names describe **what is being tested, under what condition, and what the expected result is**:

```
methodName_condition_expectedBehavior
```

Examples:
- `add_twoPositiveNumbers_returnsSum`
- `findById_userNotFound_throwsException`
- `save_validEntity_persistsAndReturnsId`

## Running tests

```bash
# Maven
mvn test

# Gradle
./gradlew test

# IntelliJ / VS Code — click the green triangle next to any @Test method
```

## Code coverage

Add JaCoCo to Maven or Gradle. A reasonable target for a service layer is 80%+ line coverage.

```xml
<!-- Maven plugin snippet -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
</plugin>
```

Run: `mvn test jacoco:report` then open `target/site/jacoco/index.html`.
