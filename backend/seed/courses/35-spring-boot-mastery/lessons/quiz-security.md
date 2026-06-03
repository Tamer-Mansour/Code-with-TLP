# Quiz: Spring Security & JWT

Test your understanding of securing Spring Boot 3 applications with Spring Security and JSON Web Tokens — covering the security filter chain, authentication, authorization, JWT structure, stateless session management, password encoding, and method-level security.

---

**Q1. In Spring Security 6, the fluent DSL method that disables the traditional `HttpSession`-based security context and makes the application stateless is:**

```java
http
    .sessionManagement(session ->
        session.sessionCreationPolicy(/* which policy? */))
```

- [ ] `SessionCreationPolicy.ALWAYS`
- [ ] `SessionCreationPolicy.IF_REQUIRED`
- [x] `SessionCreationPolicy.STATELESS`
- [ ] `SessionCreationPolicy.NEVER`

---

**Q2. Which Spring Security filter is the correct place to intercept each HTTP request, validate a JWT from the `Authorization` header, and populate the `SecurityContextHolder`?**

- [ ] `BasicAuthenticationFilter`
- [ ] `UsernamePasswordAuthenticationFilter`
- [x] A custom `OncePerRequestFilter` added before `UsernamePasswordAuthenticationFilter` in the security filter chain
- [ ] `ExceptionTranslationFilter`

---

**Q3. Examine the JWT below. What is the Base64Url-decoded content of the payload segment (the middle part)?**

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwicm9sZXMiOlsiUk9MRV9VU0VSIl0sImV4cCI6MTcxNjIzOTAyMn0
.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

- [ ] The algorithm and token type (`alg`, `typ`)
- [x] The claims — subject, roles, expiration timestamp
- [ ] The HMAC signature bytes
- [ ] The Base64-encoded secret key

---

**Q4. A developer registers the following bean. What does it accomplish in the context of Spring Security?**

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();
}
```

- [ ] It encrypts JWT tokens before signing them with HMAC-SHA256.
- [ ] It configures TLS for the embedded Tomcat server.
- [x] It provides the hashing algorithm used to encode passwords before storing them and to verify raw passwords at login.
- [ ] It replaces the default `UserDetailsService` with a BCrypt-backed implementation.

---

**Q5. Which HTTP header and value convention must a client use to send a JWT to a Spring Boot API?**

| Header | Correct value format |
|---|---|
| `Authorization` | `Bearer <token>` |
| `X-Auth-Token` | `<token>` |
| `Cookie` | `jwt=<token>` |
| `Authentication` | `JWT <token>` |

- [x] `Authorization: Bearer <token>`
- [ ] `X-Auth-Token: <token>`
- [ ] `Cookie: jwt=<token>`
- [ ] `Authentication: JWT <token>`

---

**Q6. What is wrong with the following `SecurityFilterChain` configuration?**

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            .anyRequest().permitAll()
            .requestMatchers("/api/admin/**").hasRole("ADMIN")
        );
    return http.build();
}
```

- [ ] `permitAll()` cannot be used in Spring Security 6.
- [ ] `hasRole("ADMIN")` must be written as `hasAuthority("ADMIN")`.
- [x] The more-specific matcher `requestMatchers("/api/admin/**")` comes after `anyRequest()`, so it is never evaluated — specific rules must appear before `anyRequest()`.
- [ ] The bean is missing `@EnableWebSecurity` directly on the method.

---

**Q7. A `UserDetailsService` implementation is expected to throw which exception when the username is not found, so that Spring Security can return a proper `401 Unauthorized` response?**

```java
@Override
public UserDetails loadUserByUsername(String username) {
    return userRepository.findByEmail(username)
        .map(this::toUserDetails)
        .orElseThrow(() -> new /* which exception? */(username));
}
```

- [ ] `IllegalArgumentException`
- [ ] `AuthenticationException`
- [x] `UsernameNotFoundException`
- [ ] `BadCredentialsException`

---

**Q8. Which annotation enables method-level security so that `@PreAuthorize`, `@PostAuthorize`, and `@Secured` annotations are evaluated on Spring-managed beans?**

```java
@Configuration
@EnableWebSecurity
@/* which annotation? */
public class SecurityConfig { ... }
```

- [ ] `@EnableGlobalMethodSecurity(securedEnabled = true)` — this is the only valid option
- [ ] `@EnableWebMvc`
- [x] `@EnableMethodSecurity`
- [ ] `@EnableGlobalAuthentication`

---

**Q9. A JWT is signed with a 256-bit HMAC secret. After the token is issued, an attacker intercepts it and changes the `"role"` claim in the payload from `"USER"` to `"ADMIN"` before resending it. What happens on the server?**

- [ ] The server accepts the token because it only decodes the payload without checking the signature.
- [ ] The server silently ignores unknown claim values and denies access based on the original role.
- [ ] The server throws a `NullPointerException` because the role value changed type.
- [x] Signature verification fails — the computed HMAC over the modified header and payload no longer matches the original signature, and the server rejects the token with a 401.

---

**Q10. Which `application.properties` entries are the minimum required to configure the JJWT library secret and expiration for a Spring Boot 3 JWT implementation?**

```properties
app.jwt.secret=MySuperSecretKeyThatIsAtLeast256BitsLong!!
app.jwt.expiration-ms=86400000
```

```java
@Value("${app.jwt.secret}")
private String jwtSecret;

@Value("${app.jwt.expiration-ms}")
private long jwtExpirationMs;

public String generateToken(String username) {
    return Jwts.builder()
            .subject(username)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + jwtExpirationMs))
            .signWith(Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8)))
            .compact();
}
```

- [ ] No properties are needed — JJWT auto-configures a secret from `spring.security.oauth2.resourceserver.jwt.secret-value`.
- [ ] Only `app.jwt.secret` is required; expiration defaults to 24 h automatically.
- [ ] Both values must be placed in `bootstrap.properties`, not `application.properties`.
- [x] Both custom properties must be declared in `application.properties` and bound via `@Value` (or a `@ConfigurationProperties` class) — Spring Boot does not auto-configure JJWT secrets or expiration.
