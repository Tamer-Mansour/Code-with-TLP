# Project: Secure Task API with JWT

## Overview

In this project you'll build a **stateless, JWT-secured Task API** with Spring Boot 3 and Spring Security 6. Users register, log in to receive a signed JSON Web Token, and then use that token to manage their own private to-do tasks. Every protected endpoint is guarded by a custom authentication filter that validates the token on each request — no server-side sessions.

This is the canonical "auth" service you'll build (or maintain) on almost every backend team. It ties together the whole *Security with Spring Security & JWT* module: the `SecurityFilterChain`, `UserDetailsService`, `PasswordEncoder`, a custom `OncePerRequestFilter`, and role-based access — all on top of the layered architecture (controller → service → repository) you already know.

## Learning Objectives

By the end of this project you will be able to:

- Configure a stateless `SecurityFilterChain` in Spring Security 6 (no `WebSecurityConfigurerAdapter`).
- Hash and verify passwords with `BCryptPasswordEncoder`.
- Issue, sign, and parse JWTs using the **jjwt** library.
- Authenticate requests with a custom `OncePerRequestFilter` placed before `UsernamePasswordAuthenticationFilter`.
- Implement `UserDetailsService` to load users from the database.
- Enforce ownership and role-based authorization so users see only their own data.
- Return correct status codes: `401` for missing/invalid tokens, `403` for forbidden access.

## Prerequisites & Setup

You need:

- **JDK 17+** (`java -version` reports 17 or higher)
- **Maven 3.8+**
- An HTTP client (curl, HTTPie, or Postman)

Generate the project with Spring Initializr from the command line:

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web,security,data-jpa,validation,h2 \
  -d type=maven-project \
  -d javaVersion=17 \
  -d bootVersion=3.3.0 \
  -d groupId=com.tlp \
  -d artifactId=task-api \
  -d name=task-api \
  -d packageName=com.tlp.taskapi \
  -o task-api.zip

unzip task-api.zip -d task-api
cd task-api
```

Spring Initializr has no JWT starter, so add **jjwt** to `pom.xml` manually:

```xml
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.6</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.12.6</version>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.12.6</version>
    <scope>runtime</scope>
</dependency>
```

Configure H2 and your JWT secret in `src/main/resources/application.yml`. Use a **Base64-encoded key of at least 256 bits** for HS256:

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:tasks;DB_CLOSE_DELAY=-1
  jpa:
    hibernate:
      ddl-auto: update
  h2:
    console:
      enabled: true

app:
  jwt:
    secret: "ZmFrZS1zZWNyZXQta2V5LXRoYXQtaXMtYXQtbGVhc3QtMjU2LWJpdHMtbG9uZw=="
    expiration-ms: 3600000   # 1 hour
```

## Requirements

| # | Capability | Endpoint | Access |
|---|------------|----------|--------|
| 1 | Register a user | `POST /api/auth/register` | Public |
| 2 | Log in, receive a JWT | `POST /api/auth/login` | Public |
| 3 | Create a task | `POST /api/tasks` | Authenticated |
| 4 | List my tasks | `GET /api/tasks` | Authenticated |
| 5 | Update / complete a task | `PUT /api/tasks/{id}` | Owner only |
| 6 | Delete a task | `DELETE /api/tasks/{id}` | Owner only |

Passwords are never stored in plaintext. A user may only read or modify **their own** tasks. Requests without a valid `Authorization: Bearer <token>` header to a protected endpoint return `401`.

## Step-by-Step Tasks

### 1. Model users and tasks

- [ ] Create a `User` entity (`id`, unique `username`, hashed `password`, `role`).
- [ ] Create a `Task` entity with a `@ManyToOne` link to its owner.

```java
@Entity
@Table(name = "tasks")
public class Task {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    private boolean completed;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "owner_id")
    private User owner;
    // getters & setters
}
```

### 2. Implement UserDetailsService

- [ ] Add `UserRepository extends JpaRepository<User, Long>` with `findByUsername`.
- [ ] Implement `UserDetailsService` to load a user and map its role to an authority.

```java
@Service
public class AppUserDetailsService implements UserDetailsService {
    private final UserRepository users;
    public AppUserDetailsService(UserRepository users) { this.users = users; }

    @Override
    public UserDetails loadUserByUsername(String username) {
        User u = users.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException(username));
        return org.springframework.security.core.userdetails.User
            .withUsername(u.getUsername())
            .password(u.getPassword())
            .authorities("ROLE_" + u.getRole())
            .build();
    }
}
```

### 3. Build the JWT service

- [ ] Sign tokens with the configured secret and expiry.
- [ ] Extract the username and validate signature/expiry.

```java
@Service
public class JwtService {
    private final SecretKey key;
    private final long expirationMs;

    public JwtService(@Value("${app.jwt.secret}") String secret,
                      @Value("${app.jwt.expiration-ms}") long expirationMs) {
        this.key = Keys.hmacShaKeyFor(Decoders.BASE64.decode(secret));
        this.expirationMs = expirationMs;
    }

    public String generate(String username) {
        Date now = new Date();
        return Jwts.builder()
            .subject(username)
            .issuedAt(now)
            .expiration(new Date(now.getTime() + expirationMs))
            .signWith(key)
            .compact();
    }

    public String extractUsername(String token) {
        return Jwts.parser().verifyWith(key).build()
            .parseSignedClaims(token).getPayload().getSubject();
    }
}
```

### 4. Add the authentication filter

- [ ] Read the `Authorization: Bearer` header, validate the token, and populate the `SecurityContext`.

```java
@Component
public class JwtAuthFilter extends OncePerRequestFilter {
    private final JwtService jwt;
    private final UserDetailsService uds;
    // constructor injection omitted

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res,
                                    FilterChain chain) throws ServletException, IOException {
        String header = req.getHeader(HttpHeaders.AUTHORIZATION);
        if (header != null && header.startsWith("Bearer ")
                && SecurityContextHolder.getContext().getAuthentication() == null) {
            try {
                String username = jwt.extractUsername(header.substring(7));
                UserDetails user = uds.loadUserByUsername(username);
                var auth = new UsernamePasswordAuthenticationToken(
                    user, null, user.getAuthorities());
                SecurityContextHolder.getContext().setAuthentication(auth);
            } catch (JwtException ignored) { /* leave context empty -> 401 */ }
        }
        chain.doFilter(req, res);
    }
}
```

### 5. Wire up the security configuration

- [ ] Make the chain stateless, permit `/api/auth/**`, secure everything else, and register the filter.

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    SecurityFilterChain chain(HttpSecurity http, JwtAuthFilter jwtFilter) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**", "/h2-console/**").permitAll()
                .anyRequest().authenticated())
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }

    @Bean PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(); }

    @Bean AuthenticationManager authManager(AuthenticationConfiguration c) throws Exception {
        return c.getAuthenticationManager();
    }
}
```

### 6. Expose auth and task endpoints

- [ ] On register, encode the password with the `PasswordEncoder` before saving.
- [ ] On login, authenticate via `AuthenticationManager`, then return a token.
- [ ] In `TaskController`, derive the current user from the `Authentication` and scope queries to that owner.

```java
@PostMapping("/login")
public Map<String, String> login(@Valid @RequestBody LoginRequest req) {
    authManager.authenticate(
        new UsernamePasswordAuthenticationToken(req.username(), req.password()));
    return Map.of("token", jwt.generate(req.username()));
}
```

### 7. Verify it works

```bash
# Register, then log in to capture a token
curl -X POST localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}'

TOKEN=$(curl -s -X POST localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}' | sed 's/.*"token":"\([^"]*\)".*/\1/')

curl -X POST localhost:8080/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Ship the API"}'
```

## Acceptance Criteria

- [ ] `POST /api/auth/register` stores a **BCrypt-hashed** password (never plaintext).
- [ ] `POST /api/auth/login` returns a valid signed JWT; wrong credentials return `401`.
- [ ] Protected endpoints with no/invalid/expired token return `401`.
- [ ] `GET /api/tasks` returns only the authenticated user's tasks.
- [ ] Updating or deleting another user's task returns `403` (or `404`).
- [ ] The security chain is **stateless** (`SessionCreationPolicy.STATELESS`).
- [ ] `JwtAuthFilter` runs **before** `UsernamePasswordAuthenticationFilter`.

## Stretch Challenges

1. Add **refresh tokens** with a longer expiry and a `POST /api/auth/refresh` endpoint.
2. Add an `ADMIN` role and an admin-only endpoint guarded by `@PreEnable`/`@PreAuthorize("hasRole('ADMIN')")`.
3. Implement **logout via a token denylist** stored in Redis or an in-memory set.
4. Return RFC 7807 `ProblemDetail` bodies from a custom `AuthenticationEntryPoint`.
5. Add **rate limiting** on `/api/auth/login` to slow brute-force attempts.

## Hints

- The HS256 secret **must** decode to at least 256 bits, or `Keys.hmacShaKeyFor` throws `WeakKeyException`.
- Don't manually compare passwords — let `AuthenticationManager.authenticate(...)` do it; it uses your `PasswordEncoder` and `UserDetailsService` automatically.
- To enforce ownership, filter at the repository (`findByIdAndOwnerUsername(...)`) rather than loading then checking — it closes the `404` vs `403` information-leak gap.
- The H2 console renders in frames; if you enable it, add `http.headers(h -> h.frameOptions(f -> f.sameOrigin()))`.
- A missing token should leave the `SecurityContext` empty so Spring's default entry point returns `401` — never throw your own exception from the filter.
```