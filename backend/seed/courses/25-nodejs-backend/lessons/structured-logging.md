# Structured Logging with Pino

`console.log` is fine for scripts but insufficient for production APIs. You need logs that are:

- **Structured** (JSON) so log aggregators (Datadog, Loki, CloudWatch) can query them.
- **Leveled** so you can filter noise in production.
- **Fast** so logging doesn't become a bottleneck.

**Pino** is the fastest production logger for Node, and the de-facto standard for Express/Fastify APIs.

## Install

```bash
npm install pino pino-http
npm install -D pino-pretty   # pretty-print for local dev only
```

## Basic Setup

```js
// lib/logger.js
import pino from "pino";

const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
  ...(process.env.NODE_ENV !== "production" && {
    transport: { target: "pino-pretty" },
  }),
});

export default logger;
```

## Log Levels

| Level | Value | Use for |
|-------|-------|---------|
| `trace` | 10 | Very verbose debugging |
| `debug` | 20 | Developer-facing details |
| `info` | 30 | Normal business events |
| `warn` | 40 | Unexpected but recoverable |
| `error` | 50 | Errors that need attention |
| `fatal` | 60 | App is about to crash |

In production, set `LOG_LEVEL=info` (or `warn`) to silence `debug` and `trace`.

## Logging in Practice

```js
import logger from "./lib/logger.js";

// Simple message
logger.info("Server started on port 3000");

// Structured fields — first arg is an object
logger.info({ userId: "u123", action: "login" }, "User logged in");

// Error with full stack
try {
  await db.query(sql);
} catch (err) {
  logger.error({ err, sql }, "Database query failed");
}

// Child logger — inherits fields (great for request-scoped logging)
const requestLogger = logger.child({ requestId: "abc-123" });
requestLogger.info("Processing payment");    // every message includes requestId
```

## HTTP Request Logging with pino-http

```js
import pinoHttp from "pino-http";
import logger from "./lib/logger.js";

app.use(pinoHttp({
  logger,
  customLogLevel(req, res, err) {
    if (res.statusCode >= 500) return "error";
    if (res.statusCode >= 400) return "warn";
    return "info";
  },
  serializers: {
    req(req) {
      return { method: req.method, url: req.url };  // omit headers/body for brevity
    },
  },
}));
```

Each request automatically logs: method, URL, status code, response time, request ID.

## Avoid These Patterns

```js
// BAD: unstructured, hard to query in a log aggregator
console.log("User " + userId + " logged in at " + new Date());

// GOOD: structured, queryable by userId/timestamp
logger.info({ userId }, "User logged in");
```

```js
// BAD: logging sensitive data
logger.info({ password, token }, "Login attempt");

// GOOD: never log secrets
logger.info({ email }, "Login attempt");
```

## Log Correlation — Request IDs

Attach a unique `requestId` to every incoming request so you can trace all log lines for a single request:

```js
import { randomUUID } from "node:crypto";

app.use((req, res, next) => {
  req.requestId = req.headers["x-request-id"] ?? randomUUID();
  res.setHeader("x-request-id", req.requestId);
  next();
});
```

Pass `req.requestId` into child loggers and include it in error responses.

## What to Log

| Event | Level |
|-------|-------|
| Server started | `info` |
| HTTP request received | `info` (via pino-http) |
| User logged in/out | `info` |
| Validation failed (client error) | `warn` |
| Failed DB query | `error` |
| Unexpected exception | `error` |
| Service shutting down | `info` |
| Crash / unhandled rejection | `fatal` |

Structure is more important than verbosity. A focused `error` log with context (`userId`, `requestId`, `err.message`) is worth more than ten `console.log` lines.
