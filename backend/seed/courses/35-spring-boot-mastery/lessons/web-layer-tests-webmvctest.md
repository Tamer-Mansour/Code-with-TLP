# Web Layer Tests with @WebMvcTest

When you only want to test your controllers — request mapping, validation, JSON serialization, and HTTP status codes — booting the full application context is wasteful. Spring Boot's `@WebMvcTest` is a **slice test** that loads only the web layer: your `@Controller`/`@RestController` beans, `@ControllerAdvice`, converters, and Spring Security filters. It skips `@Service`, `@Repository`, and `@Component` beans entirely.

## What gets loaded

| Loaded | Not loaded |
| --- | --- |
| `@Controller`, `@RestController` | `@Service`, `@Component` |
| `@ControllerAdvice`, filters | `@Repository`, JPA/DataSource |
| `MockMvc`, Jackson, validation | Full `@SpringBootApplication` context |

Because collaborators like services are excluded, you provide them as mocks. The auto-configured `MockMvc` lets you fire fake HTTP requests without a running server, making these tests fast and focused.

## A worked example

Given a simple controller:

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    public UserDto getUser(@PathVariable Long id) {
        return userService.findById(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public UserDto create(@Valid @RequestBody CreateUserRequest req) {
        return userService.create(req.name());
    }
}
```

The slice test mocks the service and drives `MockMvc`:

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockitoBean
    private UserService userService;

    @Test
    void getUser_returnsUser() throws Exception {
        given(userService.findById(1L))
                .willReturn(new UserDto(1L, "Ada"));

        mockMvc.perform(get("/api/users/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Ada"));
    }

    @Test
    void create_withBlankName_returns400() throws Exception {
        var body = objectMapper.writeValueAsString(
                new CreateUserRequest(""));

        mockMvc.perform(post("/api/users")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isBadRequest());
    }
}
```

> Note: `@MockitoBean` (Spring Boot 3.4+) replaces the now-deprecated `@MockBean`. On older 3.x versions, use `@MockBean` from `org.springframework.boot.test.mock.mockito`.

Static imports come from `MockMvcRequestBuilders` (`get`, `post`), `MockMvcResultMatchers` (`status`, `jsonPath`), and Mockito's `BDDMockito.given`.

## Narrowing and configuring the slice

- `@WebMvcTest(UserController.class)` loads **only** that controller. With no argument, it scans all `@Controller` beans — slower and more brittle. Prefer naming the controller.
- Add `@Import(...)` to pull in a specific `@ControllerAdvice` or converter the test needs.
- If Spring Security is on the classpath, filters are applied. Either supply a test user or disable security per request:

```java
mockMvc.perform(get("/api/users/1")
        .with(SpringSecurityMockMvcRequestPostProcessors.user("test")))
        .andExpect(status().isOk());
```

## Common mistakes and best practices

- **Wiring real services.** Any non-web bean must be a mock; otherwise the context fails to start with a missing-bean error.
- **Forgetting `contentType`.** A `@RequestBody` endpoint needs `APPLICATION_JSON` or you'll get `415 Unsupported Media Type`.
- **Unexpected 401/403.** Security auto-config still runs. Authenticate the request or configure a test security setup.
- **Using `@WebMvcTest` for repository logic.** It loads no persistence layer — use `@DataJpaTest` for that.
- **Add `.andDo(print())`** while debugging to dump the full request/response.

## Summary

`@WebMvcTest` is a fast, focused slice that loads just the web layer, letting you verify controller behavior with `MockMvc` and mocked collaborators. Name the controller under test, mock its dependencies with `@MockitoBean`, and account for security filters.
