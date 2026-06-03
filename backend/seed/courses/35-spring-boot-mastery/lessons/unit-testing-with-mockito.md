# Unit Testing Services with Mockito

Service classes hold your business logic, so they deserve fast, focused **unit tests**. A true unit test exercises one class in isolation: we run the real service code but replace its collaborators (repositories, clients, other services) with **mocks**. Mockito is the de-facto mocking library, and it ships inside `spring-boot-starter-test`, so no extra dependency is needed in a Spring Boot 3 / Maven project.

## Why mock collaborators?

A service usually depends on a repository that talks to a database. Spinning up the full Spring context or a real database for every test is slow and brittle. By mocking the repository we:

- Keep tests **fast** (milliseconds, no I/O).
- Control inputs precisely (`when(...).thenReturn(...)`).
- Verify interactions (`verify(...)`).

Crucially, a unit test of a service should **not** load the Spring context. Use plain JUnit 5 plus Mockito.

## The class under test

```java
@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User register(String email) {
        if (userRepository.existsByEmail(email)) {
            throw new IllegalStateException("Email already in use");
        }
        return userRepository.save(new User(email));
    }
}
```

## Writing the test

Annotate the test class with `@ExtendWith(MockitoExtension.class)`. Use `@Mock` for collaborators and `@InjectMocks` to build the service with those mocks injected via its constructor.

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    UserRepository userRepository;

    @InjectMocks
    UserService userService;

    @Test
    void register_savesNewUser() {
        when(userRepository.existsByEmail("a@b.com")).thenReturn(false);
        when(userRepository.save(any(User.class)))
                .thenAnswer(inv -> inv.getArgument(0));

        User result = userService.register("a@b.com");

        assertThat(result.getEmail()).isEqualTo("a@b.com");
        verify(userRepository).save(any(User.class));
    }

    @Test
    void register_rejectsDuplicateEmail() {
        when(userRepository.existsByEmail("a@b.com")).thenReturn(true);

        assertThatThrownBy(() -> userService.register("a@b.com"))
                .isInstanceOf(IllegalStateException.class);

        verify(userRepository, never()).save(any());
    }
}
```

`assertThat` / `assertThatThrownBy` come from AssertJ, also bundled with the test starter.

## Core Mockito API

| Call | Purpose |
|------|---------|
| `mock(Type.class)` | Create a mock manually |
| `when(x).thenReturn(v)` | Stub a return value |
| `when(x).thenThrow(ex)` | Stub an exception |
| `thenAnswer(inv -> ...)` | Compute the result dynamically |
| `verify(mock).method()` | Assert a call happened |
| `verify(mock, never())` | Assert it never happened |
| `verify(mock, times(2))` | Assert call count |
| `@Captor` / `ArgumentCaptor` | Capture and inspect arguments |

### Capturing arguments

When you need to inspect *what* was passed to a mock:

```java
ArgumentCaptor<User> captor = ArgumentCaptor.forClass(User.class);
verify(userRepository).save(captor.capture());
assertThat(captor.getValue().getEmail()).isEqualTo("a@b.com");
```

## Common mistakes and best practices

- **Don't use `@SpringBootTest` for unit tests.** That loads the whole context and is integration-level. Use `MockitoExtension` instead.
- **Don't mix matchers and raw values.** If one argument uses `any()`, all must use matchers: `eq("a@b.com")`, etc.
- **Avoid stubbing what you don't use.** `MockitoExtension` uses strict stubs and will fail on unnecessary stubbing, which keeps tests honest.
- **Prefer constructor injection** in services so `@InjectMocks` works cleanly and dependencies are explicit.
- **Verify behavior, not implementation details** only where it matters (e.g., that `save` was called), to avoid brittle tests.

## Summary

Mockito lets you test Spring services in isolation by replacing collaborators with mocks: stub inputs with `when().thenReturn()`, run the real service, then assert results and `verify()` interactions. Keep these tests context-free with `@ExtendWith(MockitoExtension.class)` for fast, reliable coverage of your business logic.
