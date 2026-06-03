# Method Security and Roles

URL-based security (`HttpSecurity`) protects HTTP endpoints, but it can't reach service-layer methods or scheduled jobs. **Method security** lets you enforce authorization directly on Spring beans using annotations — keeping the rule next to the code it protects.

## Enabling Method Security

In Spring Security 6 (Spring Boot 3), turn it on with `@EnableMethodSecurity` on any `@Configuration` class. It enables `@PreAuthorize`/`@PostAuthorize` by default.

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;

@Configuration
@EnableMethodSecurity // prePostEnabled = true by default
public class MethodSecurityConfig {
}
```

> `@EnableGlobalMethodSecurity` is deprecated. Use `@EnableMethodSecurity`, which is built on the modern, AOP-based `AuthorizationManager` API and supports SpEL out of the box.

## Roles vs. Authorities

A **role** is just an authority with the `ROLE_` prefix. The `hasRole('ADMIN')` check matches the authority `ROLE_ADMIN`; `hasAuthority('ROLE_ADMIN')` is equivalent. Use roles for coarse identity ("who you are") and authorities for fine-grained permissions ("what you can do", e.g. `course:delete`).

| Expression | Matches authority | Typical use |
|---|---|---|
| `hasRole('ADMIN')` | `ROLE_ADMIN` | Broad role check |
| `hasAuthority('ROLE_ADMIN')` | `ROLE_ADMIN` | Same as above, explicit |
| `hasAuthority('course:delete')` | `course:delete` | Permission check |
| `hasAnyRole('ADMIN','EDITOR')` | `ROLE_ADMIN` or `ROLE_EDITOR` | Either role |

When building your `UserDetails` (or JWT-derived authorities), store roles **with** the `ROLE_` prefix so `hasRole` works:

```java
return new SimpleGrantedAuthority("ROLE_" + role.name());
```

## @PreAuthorize and @PostAuthorize

`@PreAuthorize` runs **before** the method — the common choice. `@PostAuthorize` runs **after**, so you can inspect the return value via `returnObject`.

```java
@Service
public class CourseService {

    @PreAuthorize("hasRole('ADMIN')")
    public void deleteCourse(Long id) { /* admins only */ }

    // Combine roles and method arguments with SpEL
    @PreAuthorize("hasRole('INSTRUCTOR') and #course.ownerId == authentication.name")
    public Course updateCourse(Course course) { return repo.save(course); }

    // Validate the returned object after execution
    @PostAuthorize("returnObject.ownerId == authentication.name")
    public Course findDraft(Long id) { return repo.findById(id).orElseThrow(); }
}
```

`#course` references a method parameter by name (compile with `-parameters`, the default in Spring Boot 3 starters). `authentication` is the current `Authentication` object.

## Filtering Collections

`@PreFilter` and `@PostFilter` filter elements in or out of a collection using `filterObject`:

```java
@PostFilter("filterObject.published or hasRole('ADMIN')")
public List<Course> listCourses() {
    return repo.findAll(); // non-admins see only published courses
}
```

Note: filtering large result sets in memory is wasteful — prefer query-level filtering for big datasets and reserve `@PostFilter` for small collections.

## Common Mistakes and Best Practices

- **Calling a secured method from the same class** bypasses the proxy, so the annotation is ignored. Put secured methods on a separate bean, or inject the bean into itself.
- **Forgetting the `ROLE_` prefix** when assigning authorities — then `hasRole('ADMIN')` silently fails.
- **`@PostAuthorize` runs after side effects.** Don't use it on methods that write data; if access is denied, the write may already be committed.
- **Annotate the interface or the implementation consistently.** Mixing both can lead to confusion about which advice applies.
- Prefer `@PreAuthorize` over the older `@Secured`/JSR-250 `@RolesAllowed`, because SpEL gives you argument- and return-value-aware rules.

## Summary

Method security puts authorization where the logic lives. Enable it with `@EnableMethodSecurity`, use `@PreAuthorize` with SpEL (`hasRole`, `hasAuthority`, argument references) for most checks, and reserve `@PostAuthorize`/`@PostFilter` for return-value decisions on read-only operations.
