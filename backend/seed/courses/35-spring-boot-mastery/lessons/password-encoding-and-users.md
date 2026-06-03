# User Details and Password Encoding

Spring Security never trusts a raw password. Before it can authenticate anyone, it needs two things: a way to *load* a user (their username, hashed password, and authorities) and a way to *verify* a submitted password against the stored hash. These responsibilities are handled by `UserDetailsService` and `PasswordEncoder`.

## The core abstractions

| Type | Role |
| --- | --- |
| `UserDetails` | Read-only view of a user: username, encoded password, authorities, account flags. |
| `UserDetailsService` | Loads a `UserDetails` by username (`loadUserByUsername`). |
| `PasswordEncoder` | Hashes raw passwords and matches a raw password against a stored hash. |

The golden rule: **store hashes, never plaintext.** Spring Security's `DaoAuthenticationProvider` compares the submitted password to the stored one through the `PasswordEncoder` — it never sees the original.

## Choosing a PasswordEncoder

`BCryptPasswordEncoder` is the sensible default. It is adaptive (you can raise the cost factor as hardware improves) and includes a per-password salt automatically.

```java
@Configuration
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        // strength 12; default is 10. Higher = slower = more brute-force resistant.
        return new BCryptPasswordEncoder(12);
    }
}
```

| Encoder | Notes |
| --- | --- |
| `BCryptPasswordEncoder` | Solid default, built-in salt, tunable strength. |
| `Argon2PasswordEncoder` | Memory-hard, current best practice; needs more CPU/RAM. |
| `Pbkdf2PasswordEncoder` | FIPS-friendly option. |
| `DelegatingPasswordEncoder` | Stores an `{id}` prefix so you can migrate algorithms later. |

For new apps that may evolve, prefer the delegating encoder via the factory:

```java
@Bean
public PasswordEncoder passwordEncoder() {
    // Produces hashes prefixed like {bcrypt}$2a$10$... enabling future upgrades.
    return PasswordEncoderFactories.createDelegatingPasswordEncoder();
}
```

## Implementing UserDetailsService

Wrap your JPA entity in a `UserDetails` implementation, then return it from the service. Authorities map to roles/permissions.

```java
@Service
@RequiredArgsConstructor
public class JpaUserDetailsService implements UserDetailsService {

    private final UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String username) {
        AppUser user = userRepository.findByUsername(username)
                .orElseThrow(() ->
                    new UsernameNotFoundException("User not found: " + username));

        return User.builder()
                .username(user.getUsername())
                .password(user.getPassword())          // already BCrypt-hashed
                .authorities("ROLE_" + user.getRole())  // e.g. ROLE_ADMIN
                .accountLocked(!user.isEnabled())
                .build();
    }
}
```

`org.springframework.security.core.userdetails.User` is a ready-made `UserDetails` builder, so you rarely need to write the interface by hand.

## Encoding on registration

Always hash *when you save*, not when you authenticate.

```java
@Service
@RequiredArgsConstructor
public class RegistrationService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public AppUser register(String username, String rawPassword) {
        AppUser user = new AppUser();
        user.setUsername(username);
        user.setPassword(passwordEncoder.encode(rawPassword)); // hash here
        user.setRole("USER");
        return userRepository.save(user);
    }
}
```

The stored column then looks like:

```sql
-- password column holds the hash, never the raw value
INSERT INTO app_user (username, password, role)
VALUES ('jane', '$2a$12$Dwt1...redacted...K9u', 'USER');
```

## Common mistakes and best practices

- **Double-encoding:** calling `encode()` at registration *and* again somewhere else makes the password unverifiable. Encode exactly once.
- **Comparing manually:** never use `equals()` on passwords. Let `passwordEncoder.matches(raw, stored)` do constant-time comparison (Spring's provider calls this for you).
- **No encoder bean:** without a `PasswordEncoder` bean, modern Spring Security throws `There is no PasswordEncoder mapped for the id "null"`.
- **Storing plaintext or weak hashes (MD5/SHA-1):** unacceptable — use BCrypt or Argon2.
- **Don't leak which part failed:** return a generic `UsernameNotFoundException`; let the framework convert it to a uniform `BadCredentials` response.
- **`NoOpPasswordEncoder` is for demos only** — it is deprecated and stores plaintext.

## Summary

Implement `UserDetailsService` to load users from your database and expose a `PasswordEncoder` (BCrypt or delegating) as a bean. Hash passwords once at registration, and let Spring Security verify them with `matches()` during authentication.
