# Authentication with JWT

Two questions you'll meet on every API: **who is the user** (authentication) and **what can they do** (authorization). JWT is one common authentication mechanism for stateless APIs.

## JWT in 60 seconds

A JSON Web Token is three base64-encoded parts joined with `.`:

```
header.payload.signature
```

- **Header** — algorithm metadata.
- **Payload** — claims (user id, expiry, scopes).
- **Signature** — proves the token wasn't modified.

```json
// header
{ "alg": "HS256", "typ": "JWT" }

// payload
{ "sub": "user-42", "iat": 1700000000, "exp": 1700003600 }
```

## Issuing a token

```js
import jwt from "jsonwebtoken";

const token = jwt.sign(
  { sub: user.id, role: user.role },
  process.env.JWT_SECRET,
  { expiresIn: "15m" }
);
res.json({ accessToken: token });
```

## Verifying a token

```js
function authMiddleware(req, res, next) {
  const header = req.headers.authorization;
  if (!header?.startsWith("Bearer ")) {
    return res.status(401).json({ error: "missing token" });
  }
  try {
    const payload = jwt.verify(header.slice(7), process.env.JWT_SECRET);
    req.user = payload;
    next();
  } catch {
    res.status(401).json({ error: "invalid token" });
  }
}

app.get("/me", authMiddleware, (req, res) => {
  res.json({ id: req.user.sub });
});
```

## Refresh tokens

Short-lived access tokens (5–15 minutes) + long-lived refresh tokens (days/weeks). When the access token expires, the client trades the refresh token for a new pair.

Store refresh tokens server-side (a `sessions` table) so you can revoke them.

## Cookies vs Authorization header

- **Authorization header** — common for APIs and SPAs that store tokens in memory.
- **HttpOnly cookies** — set `Secure`, `SameSite=Strict`. Less vulnerable to XSS-token-theft, but you need CSRF protection.

For web apps, cookies often win. For native/mobile clients, headers.

## Sessions vs JWTs

JWTs **stateless** — no DB lookup per request. Trade-off: harder to revoke (must wait for expiry or keep a denylist).

Session cookies **stateful** — a session ID in the cookie, looked up in Redis or Postgres per request. Easier to revoke; one DB hit per request (Redis makes this fast).

For most apps, **session cookies with a Redis-backed store** are simpler and safer than JWT. Reach for JWT when you need cross-service auth without a session store.

## OAuth2 and OpenID Connect

Don't roll your own login for "sign in with Google/GitHub/Microsoft." Use Passport.js, Auth.js (NextAuth), or a hosted provider like Clerk, Auth0, Supabase Auth, AWS Cognito.

## Passwords

If you must store them:

- **Hash with bcrypt or argon2** (work factor 12+).
- **Never log them.**
- **Never email them.**
- Enforce a length minimum (12+), not silly composition rules.

Better: don't ask for passwords at all. Email magic links or OAuth.

## Rate limiting

```js
import rateLimit from "express-rate-limit";

app.use("/login", rateLimit({ windowMs: 60_000, max: 5 }));
```

Prevents credential stuffing. For distributed deployments, use Redis-backed rate limiters.

## Common mistakes

- Storing JWTs in `localStorage` — vulnerable to XSS. Memory or HttpOnly cookies.
- Using `alg: none` (yes, it's a JWT algorithm name) — verify a specific algorithm.
- Trusting client-provided role claims — verify on the server.
- Forgetting `exp` — tokens last forever otherwise.
