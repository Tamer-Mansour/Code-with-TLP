# Spring Security Architecture and the Filter Chain

Spring Security secures your application by inserting a chain of **servlet filters** in front of your controllers. Every HTTP request passes through this chain *before* it reaches your `@RestController`. Understanding how these filters cooperate is the key to debugging authentication issues and customizing security correctly.

## The Big Picture

A single `DelegatingFilterProxy` (registered by Spring Boot) hands each request to the `FilterChainProxy`, which selects the matching `SecurityFilterChain` and runs its ordered list of filters. The most important ones:

| Filter | Responsibility |
| --- | --- |
| `SecurityContextHolderFilter` | Loads/clears the `SecurityContext` per request |
| `UsernamePasswordAuthenticationFilter` | Handles form-login credential submission |
| `BearerTokenAuthenticationFilter` | Reads JWT/OAuth2 bearer tokens (resource server) |
| `ExceptionTranslationFilter` | Converts `AccessDeniedException`/`AuthenticationException` into 401/403 |
| `AuthorizationFilter` | Final gate; enforces access rules and throws on denial |

If any filter authenticates the request, it stores an `Authentication` object in the `SecurityContextHolder`. Downstream filters and your controllers read from there.

## Core Concepts

- **`Authentication`** — represents the principal (who) plus granted authorities (what they can do).
- **`SecurityContextHolder`** — thread-local storage holding the current `Authentication`.
- **`AuthenticationManager`** — delegates to `AuthenticationProvider`s to verify credentials.
- **`UserDetailsService`** — loads a user by username for password-based auth.

## Configuring the Chain (Spring Boot 3 / Security 6)

In Spring Security 6 you define a `SecurityFilterChain` bean using the lambda DSL. The older `WebSecurityConfigurerAdapter` is **removed** — do not look for it.

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import static org.springframework.security.config.Customizer.withDefaults;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // disable only for stateless APIs
            .sessionManagement(sm -> sm
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**", "/actuator/health").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated())
            .httpBasic(withDefaults());
        return http.build();
    }
}
```

Order matters: `authorizeHttpRequests` rules are evaluated **top to bottom**, and the first match wins. Always put the most specific paths first and end with `anyRequest()`.

## Adding a Custom Filter

For JWT you typically insert your own filter *before* the username/password filter so the token is validated early:

```java
http.addFilterBefore(jwtAuthFilter,
        UsernamePasswordAuthenticationFilter.class);
```

A minimal custom filter extends `OncePerRequestFilter`, ensuring it runs exactly once per request:

```java
import jakarta.servlet.FilterChain;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.filter.OncePerRequestFilter;

public class JwtAuthFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req,
                                    HttpServletResponse res,
                                    FilterChain chain)
            throws java.io.IOException, jakarta.servlet.ServletException {
        // validate token, build Authentication, set it on the context...
        chain.doFilter(req, res); // ALWAYS continue the chain
    }
}
```

Note the `jakarta.servlet.*` imports — Spring Boot 3 moved off `javax`.

## Common Mistakes and Best Practices

- **Forgetting `chain.doFilter(...)`** silently swallows the request — nothing downstream runs.
- **Leaving CSRF enabled for a token-based API** breaks POST/PUT calls; disable it only when you are stateless.
- **Using `hasRole("ROLE_ADMIN")`** — `hasRole` adds the `ROLE_` prefix automatically; pass `"ADMIN"`.
- **Putting `anyRequest().permitAll()` first** makes all later rules dead code.
- Keep filter chains **stateless** for REST APIs (`SessionCreationPolicy.STATELESS`) and never store secrets in the `SecurityContext`.

## Summary

Spring Security is a configurable chain of servlet filters that builds and enforces an `Authentication` stored in the `SecurityContextHolder`. In Spring Boot 3 you wire it through a `SecurityFilterChain` bean and slot custom logic (like JWT validation) into the chain with `addFilterBefore`.
