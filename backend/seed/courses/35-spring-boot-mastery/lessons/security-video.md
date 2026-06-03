# Video: Spring Security and JWT

This video walks through securing a Spring Boot 3 REST API end-to-end using Spring Security 6 and stateless JWT-based authentication.

## What you'll learn

- How Spring Security's filter chain processes every incoming HTTP request
- Configuring a `SecurityFilterChain` bean with `HttpSecurity` to disable sessions and require bearer tokens
- Generating and signing JWTs with `io.jsonwebtoken` (JJWT) and a secret key
- Writing a `OncePerRequestFilter` that validates the token and populates the `SecurityContext`
- Protecting endpoints with role-based rules (`hasRole`, `hasAuthority`)
- Testing secured endpoints with Postman or `MockMvc`

## Key takeaways

- Spring Security 6 uses a lambda-style DSL — `http.csrf(AbstractHttpConfigurer::disable)` replaces the old `.csrf().disable()` chaining style
- JWTs should be short-lived (15 min access token) paired with a longer-lived refresh token
- Never store the JWT secret in source control; externalise it via `application.properties` or an environment variable

## Follow-along checklist

- [ ] Add `spring-boot-starter-security` and `jjwt-api` / `jjwt-impl` dependencies to `pom.xml`
- [ ] Create `JwtUtil`, `JwtFilter`, and `SecurityConfig` classes
- [ ] Expose `/api/auth/login` as a public endpoint and lock down everything else
- [ ] Smoke-test with a valid and an expired token to confirm 200 vs 401 responses

The link in this lesson opens a curated YouTube search returning free, high-quality videos from channels such as freeCodeCamp and Amigoscode covering exactly this Spring Security + JWT workflow.
