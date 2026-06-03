# Introduction to JWT Authentication

When you build a backend with Spring, you need a way to know **who** is making each request. JSON Web Tokens (JWT) are the most common answer for stateless REST APIs. Instead of the server remembering a session in memory, the client carries a signed token on every request that proves its identity.

## What is a JWT?

A JWT is a compact, URL-safe string made of three Base64URL-encoded parts separated by dots:

```
header.payload.signature
```

- **Header** — the signing algorithm, e.g. `{"alg":"HS256","typ":"JWT"}`.
- **Payload** — the *claims*: data about the user such as `sub` (subject/username), `exp` (expiry), `iat` (issued-at), and any custom fields like roles.
- **Signature** — an HMAC/RSA signature over the header and payload, created with a secret key. It lets the server verify the token was not tampered with.

A decoded payload looks like this:

```json
{
  "sub": "tlp-student",
  "roles": ["USER"],
  "iat": 1717372800,
  "exp": 1717376400
}
```

> Important: the payload is only **encoded**, not **encrypted**. Anyone can read it. Never put passwords or secrets inside a JWT.

## The authentication flow

1. The user POSTs credentials to `/api/auth/login`.
2. The server validates them against MySQL and, if valid, signs a JWT and returns it.
3. The client stores the token and sends it on every protected request via the header:

```http
Authorization: Bearer <token>
```

4. The server verifies the signature and expiry, then trusts the claims — no database lookup for the session is required.

## Sessions vs JWT

| Aspect            | Server Sessions            | JWT                          |
|-------------------|----------------------------|------------------------------|
| State             | Stored on server           | Stateless (held by client)   |
| Scaling           | Needs shared session store | Scales horizontally easily   |
| Revocation        | Delete the session         | Hard — must wait for expiry  |
| Storage location  | Cookie + server memory/DB  | Header / cookie on client    |

## Creating and verifying a token in Java

With Spring projects we use the **jjwt** library. Add it to `pom.xml`:

```xml
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.6</version>
</dependency>
```

A small helper that generates and validates tokens:

```java
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import javax.crypto.SecretKey;
import java.util.Date;

public class JwtUtil {

    // Use a strong secret (>= 32 bytes for HS256), loaded from config in real apps.
    private final SecretKey key =
            Keys.hmacShaKeyFor("change-this-to-a-long-random-secret-key!".getBytes());

    public String generateToken(String username) {
        long nowMillis = System.currentTimeMillis();
        return Jwts.builder()
                .subject(username)
                .issuedAt(new Date(nowMillis))
                .expiration(new Date(nowMillis + 3_600_000)) // 1 hour
                .signWith(key)
                .compact();
    }

    public String extractUsername(String token) {
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token) // throws if signature/expiry invalid
                .getPayload()
                .getSubject();
    }
}
```

`parseSignedClaims` throws an exception when the signature is wrong or the token has expired, which is exactly the security check you want.

## Common mistakes and best practices

- **Keep the secret out of code.** Load it from `application.properties` or an environment variable, never commit it.
- **Always set a short expiry** (`exp`). Use refresh tokens for longer sessions.
- **Verify before trusting.** Never read claims without verifying the signature first.
- **Use HTTPS** so tokens cannot be sniffed in transit.
- **Don't store sensitive data** in the payload — it is readable by anyone.

## Summary

A JWT is a signed, self-contained token that lets a Spring backend authenticate requests without server-side sessions. The server signs it at login and verifies the signature and expiry on each protected call.
