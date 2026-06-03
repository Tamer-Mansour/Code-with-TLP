# Authentication vs Authorization

These two words are used interchangeably in everyday conversation, but in security engineering they mean entirely different things. Confusing them leads to broken access-control designs. This lesson draws a hard line between them and shows exactly how Spring Security 6 models each concept.

## The Core Distinction

| Concept | Question it answers | Spring Security abstraction |
|---|---|---|
| **Authentication** | *Who are you?* | `Authentication` object in `SecurityContext` |
| **Authorization** | *What are you allowed to do?* | `GrantedAuthority` / method security / access rules |

Authentication always happens first. Authorization is meaningless without a verified identity.

## Authentication in Spring Security 6

When a request arrives, Spring Security runs it through a chain of `Filter` implementations. The relevant one for JWT-based APIs is a custom filter you register — typically extending `OncePerRequestFilter`.

After a successful login, the application issues a JWT. On every subsequent request the client sends that token in the `Authorization` header, and the filter validates it and populates the `SecurityContext`.

```java
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
            throws ServletException, IOException {

        String authHeader = request.getHeader(HttpHeaders.AUTHORIZATION);

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        String token = authHeader.substring(7);
        String username = jwtService.extractUsername(token);

        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            UserDetails userDetails = userDetailsService.loadUserByUsername(username);

            if (jwtService.isTokenValid(token, userDetails)) {
                UsernamePasswordAuthenticationToken authToken =
                        new UsernamePasswordAuthenticationToken(
                                userDetails,
                                null,
                                userDetails.getAuthorities()   // roles go here
                        );
                authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(authToken);
            }
        }

        filterChain.doFilter(request, response);
    }
}
```

Key points:
- The filter extracts the token, validates the signature and expiry, and then calls `SecurityContextHolder.getContext().setAuthentication(...)`.
- Once that line executes, the current request is considered **authenticated**. Every downstream component (controllers, services) can call `SecurityContextHolder.getContext().getAuthentication()` to retrieve the principal.
- The filter never throws an exception for an invalid token — it simply skips setting the authentication. The framework then returns `401 Unauthorized` automatically because a protected resource requires an authenticated principal.

## Authorization in Spring Security 6

Authorization is enforced after authentication. Spring Security gives you two places to apply it.

### 1. HTTP-level rules in `SecurityFilterChain`

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity          // enables @PreAuthorize / @PostAuthorize
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        return http
                .csrf(AbstractHttpConfigurer::disable)
                .sessionManagement(sm ->
                        sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/auth/**").permitAll()       // public
                        .requestMatchers("/api/admin/**").hasRole("ADMIN") // role-gated
                        .anyRequest().authenticated()                      // everything else needs auth
                )
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
                .build();
    }
}
```

### 2. Method-level rules with `@PreAuthorize`

```java
@RestController
@RequestMapping("/api/courses")
@RequiredArgsConstructor
public class CourseController {

    private final CourseService courseService;

    @GetMapping
    public List<CourseDto> list() {
        return courseService.findAll();   // any authenticated user
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")    // only ADMINs may delete
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        courseService.delete(id);
        return ResponseEntity.noContent().build();
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasRole('INSTRUCTOR') or hasRole('ADMIN')")
    public CourseDto update(@PathVariable Long id,
                            @Valid @RequestBody UpdateCourseRequest request) {
        return courseService.update(id, request);
    }
}
```

`@PreAuthorize` is evaluated before the method body runs. A failed check throws `AccessDeniedException`, which Spring Security translates to `403 Forbidden`.

## What the HTTP Status Codes Tell You

| Status | Meaning | Cause in Spring Security |
|---|---|---|
| `401 Unauthorized` | Not authenticated | No valid JWT, expired token, or missing `Authorization` header |
| `403 Forbidden` | Authenticated but not authorized | Valid JWT but the user's roles do not satisfy the access rule |

A very common mistake is returning `403` when the user is simply not logged in. Spring Security handles this correctly by default — make sure you do not suppress `AuthenticationEntryPoint`.

## Roles and Authorities

`GrantedAuthority` is the interface Spring Security uses for both roles and fine-grained permissions. By convention, roles are prefixed with `ROLE_`:

```java
List<GrantedAuthority> authorities = List.of(
    new SimpleGrantedAuthority("ROLE_ADMIN"),
    new SimpleGrantedAuthority("ROLE_INSTRUCTOR")
);
```

`hasRole("ADMIN")` in SpEL automatically prepends `ROLE_`, so `hasRole("ADMIN")` matches `ROLE_ADMIN`. `hasAuthority("ROLE_ADMIN")` requires the full string.

## Common Mistakes

- **Mixing 401 and 403** — Return `401` when identity cannot be established, `403` when it can but access is denied.
- **Storing roles in the JWT but not loading them into `UsernamePasswordAuthenticationToken`** — Pass `userDetails.getAuthorities()` as the third argument (shown above) so method security works.
- **Skipping `@EnableMethodSecurity`** — `@PreAuthorize` annotations are silently ignored without this annotation on your configuration class.
- **Permitting all requests in the filter chain and relying solely on method security** — Defence in depth: use both layers. HTTP rules block unauthenticated traffic early; method security adds fine-grained control inside the application.

## Summary

Authentication establishes *who* is making a request (verified by validating a JWT and populating the `SecurityContext`); authorization decides *what* that principal may do (enforced via `authorizeHttpRequests` rules and `@PreAuthorize` annotations). Spring Security 6 cleanly separates these two concerns across its filter chain and method-security layer.
