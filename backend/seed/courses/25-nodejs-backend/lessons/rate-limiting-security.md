# Rate Limiting and API Security

Exposing an API without rate limiting is an invitation for abuse — scrapers, brute-force attacks, and accidental denial-of-service from runaway clients. This lesson covers the essential security layers every Node API needs.

## Rate Limiting with express-rate-limit

```bash
npm install express-rate-limit
```

```js
import rateLimit from "express-rate-limit";

// Global limiter — all endpoints
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,   // 15 minutes
  max: 500,                    // max 500 requests per window per IP
  standardHeaders: true,       // Return rate limit info in RateLimit-* headers
  legacyHeaders: false,
  message: { error: "Too many requests, please try again later." },
});

// Stricter limiter for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  message: { error: "Too many login attempts." },
});

app.use(globalLimiter);
app.post("/auth/login", authLimiter, loginHandler);
```

By default, `express-rate-limit` stores counters in memory — fine for a single instance. For multi-instance deployments, use a Redis store:

```bash
npm install rate-limit-redis ioredis
```

```js
import { RedisStore } from "rate-limit-redis";
import Redis from "ioredis";

const redis = new Redis(process.env.REDIS_URL);
const limiter = rateLimit({
  windowMs: 60_000,
  max: 100,
  store: new RedisStore({ sendCommand: (...args) => redis.call(...args) }),
});
```

## Security Headers with Helmet

Helmet sets HTTP response headers that defend against common web vulnerabilities:

```bash
npm install helmet
```

```js
import helmet from "helmet";

app.use(helmet());
```

What it sets by default:

| Header | Purpose |
|--------|---------|
| `Content-Security-Policy` | Restricts sources for scripts, styles, etc. |
| `X-Frame-Options: DENY` | Prevents clickjacking |
| `X-Content-Type-Options: nosniff` | Prevents MIME sniffing |
| `Strict-Transport-Security` | Forces HTTPS (HSTS) |
| `X-XSS-Protection: 0` | Disables outdated XSS filter (CSP is better) |

## CORS Configuration

```bash
npm install cors
```

```js
import cors from "cors";

const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(",") ?? [];

app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error("CORS not allowed"));
    }
  },
  credentials: true,
  methods: ["GET", "POST", "PUT", "PATCH", "DELETE"],
}));
```

Never use `cors({ origin: "*" })` for an API that handles authentication.

## Body Size Limits

Protect against oversized payloads that exhaust memory:

```js
app.use(express.json({ limit: "100kb" }));    // reject JSON > 100 KB
app.use(express.urlencoded({ extended: true, limit: "100kb" }));
```

## Sensitive Data in Responses

- Never return passwords, hashes, or tokens in API responses.
- Use a DTO (Data Transfer Object) pattern or a `toPublic()` method:

```js
class User {
  toPublic() {
    return { id: this.id, name: this.name, email: this.email };
    // omits: passwordHash, resetToken, internalFlags
  }
}
```

## Environment Secrets

Never hard-code secrets. Load them from environment variables:

```bash
npm install dotenv
```

```js
// load BEFORE importing anything that reads env
import "dotenv/config";

const secret = process.env.JWT_SECRET;
if (!secret) throw new Error("JWT_SECRET is not set");
```

Use `.env` for local dev and never commit it. Use secrets managers (AWS Secrets Manager, Vault, Railway secrets) in production.

## Checklist

- [ ] Rate limit all public endpoints; tighten limits on auth routes.
- [ ] Use Helmet for security headers.
- [ ] Restrict CORS to known origins.
- [ ] Limit body size.
- [ ] Never log or return secrets / password hashes.
- [ ] Validate and sanitize all input (see Input Validation lesson).
- [ ] Run `npm audit` in CI.
