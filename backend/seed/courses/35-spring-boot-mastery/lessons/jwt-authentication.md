# JWT Authentication End to End

JSON Web Tokens (JWT) let a Spring Boot 3 API stay **stateless**: instead of storing a server-side session, the server issues a signed token the client sends on every request. This lesson walks the full flow on Java 17+ — login, signing, validating, and protecting endpoints.

## The Flow at a Glance

| Step | Who | What happens |
|------|-----|--------------|
| 1 | Client | POSTs username + password to `/api/auth/login` |
| 2 | Server | Authenticates, then signs a JWT and returns it |
| 3 | Client | Sends `Authorization: Bearer <token>` on each call |
| 4 | Filter | Validates signature + expiry, sets `SecurityContext` |
| 5 | Server | Serves the protected resource |

A JWT has three Base64url parts — **header.payload.signature**. Only the signature is secret-protected; the payload is *readable by anyone*, so never put passwords or secrets in claims.

## Dependencies

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
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

## Generating and Validating Tokens

```java
@Service
public class JwtService {

    @Value("${app.jwt.secret}") // Base64, at least 256 bits for HS256
    private String secret;
    private final long expirationMs = 3_600_000; // 1 hour

    private SecretKey key() {
        return Keys.hmacShaKeyFor(Decoders.BASE64.decode(secret));
    }

    public String generateToken(UserDetails user) {
        return Jwts.builder()
                .subject(user.getUsername())
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + expirationMs))
                .signWith(key())
                .compact();
    }

    public String extractUsername(String token) {
        return parse(token).getPayload().getSubject();
    }

    public boolean isValid(String token, UserDetails user) {
        var claims = parse(token).getPayload();
        return claims.getSubject().equals(user.getUsername())
                && claims.getExpiration().after(new Date());
    }

    private Jws<Claims> parse(String token) {
        return Jwts.parser().verifyWith(key()).build().parseSignedClaims(token);
    }
}
```

## The Authentication Filter

This `OncePerRequestFilter` runs on every request, reads the bearer token, and populates the security context.

```java
@Component
@RequiredArgsConstructor
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {
        final String header = request.getHeader("Authorization");
        if (header == null || !header.startsWith("Bearer ")) {
            chain.doFilter(request, response);
            return;
        }
        final String token = header.substring(7);
        final String username = jwtService.extractUsername(token);

        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            UserDetails user = userDetailsService.loadUserByUsername(username);
            if (jwtService.isValid(token, user)) {
                var auth = new UsernamePasswordAuthenticationToken(
                        user, null, user.getAuthorities());
                auth.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(auth);
            }
        }
        chain.doFilter(request, response);
    }
}
```

## Wiring the Security Chain

```java
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthFilter jwtAuthFilter;

    @Bean
    SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .anyRequest().authenticated())
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }
}
```

## Common Mistakes and Best Practices

- **Disabling CSRF blindly:** acceptable for stateless token APIs, but never for cookie-session apps.
- **Weak secrets:** HS256 requires a key of at least 256 bits, or `Keys.hmacShaKeyFor` throws.
- **Long-lived tokens:** keep access tokens short (15–60 min) and pair them with a refresh-token endpoint; you cannot revoke a stateless JWT before it expires.
- **Trusting the payload:** always `verifyWith(key())` before reading claims — never decode without verifying the signature.
- **Storing tokens insecurely:** on the client, prefer `HttpOnly` cookies or memory over `localStorage` to limit XSS exposure.

## Summary

A JWT API authenticates once, signs a short-lived token, and a `OncePerRequestFilter` validates that token on every subsequent request — keeping the server stateless. Sign with a strong key, verify before trusting any claim, and keep token lifetimes short.
