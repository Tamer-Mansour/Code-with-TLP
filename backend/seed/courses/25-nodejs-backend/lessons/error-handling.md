# Error Handling in Express

Proper error handling separates production-quality APIs from toy projects. In Node.js, unhandled errors crash the process; in Express, unhandled errors silently hang client connections.

## Synchronous vs Async Errors

Express 4 catches synchronous throws automatically but **does not** catch async errors:

```js
// Synchronous — Express catches this automatically
app.get("/sync", (req, res) => {
  throw new Error("boom");           // caught by Express error middleware
});

// Async — you MUST call next(err)
app.get("/async", async (req, res, next) => {
  try {
    const data = await fetchData();
    res.json(data);
  } catch (err) {
    next(err);                        // pass to error middleware
  }
});
```

Express 5 (currently RC) fixes this — `async` handlers are awaited and their rejections forwarded automatically. Until then, wrap every async handler.

## A Reusable Async Wrapper

```js
// lib/asyncHandler.js
export const asyncHandler = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

// Usage
import { asyncHandler } from "../lib/asyncHandler.js";

router.get("/:id", asyncHandler(async (req, res) => {
  const user = await userService.find(req.params.id);
  if (!user) throw new NotFoundError("User not found");
  res.json(user);
}));
```

## Custom Error Classes

Create domain-specific error types to centralize status codes and messages:

```js
// lib/errors.js
export class AppError extends Error {
  constructor(message, statusCode = 500) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;   // distinguish from programmer errors
  }
}

export class NotFoundError extends AppError {
  constructor(message = "Not found") { super(message, 404); }
}

export class ValidationError extends AppError {
  constructor(message = "Validation failed") { super(message, 400); }
}

export class UnauthorizedError extends AppError {
  constructor(message = "Unauthorized") { super(message, 401); }
}
```

## Central Error Middleware

Express error middleware takes **four arguments** — Express identifies it by arity:

```js
// middleware/errorHandler.js
export function errorHandler(err, req, res, next) {
  // Operational errors: expected failure paths (not found, bad input)
  if (err.isOperational) {
    return res.status(err.statusCode).json({
      error: err.message,
    });
  }

  // Programmer errors: bugs, unexpected states — log and return generic 500
  console.error("UNHANDLED ERROR", err);
  res.status(500).json({ error: "Internal server error" });
}

// app.js — must be registered AFTER all routes
import { errorHandler } from "./middleware/errorHandler.js";
app.use(errorHandler);
```

## Handling 404 Routes

Add a catch-all after your routes for unknown paths:

```js
// after all routes, before errorHandler
app.use((req, res) => {
  res.status(404).json({ error: `Route ${req.method} ${req.path} not found` });
});
```

## Global Safety Net

Catch truly unhandled rejections and uncaught exceptions at the process level:

```js
// server.js
process.on("unhandledRejection", (reason) => {
  console.error("Unhandled rejection", reason);
  process.exit(1);   // let a process manager restart cleanly
});

process.on("uncaughtException", (err) => {
  console.error("Uncaught exception", err);
  process.exit(1);
});
```

In production, run Node under a process manager (PM2, systemd, or a container restart policy) so the process restarts automatically.

## Error Response Shape

Be consistent. A typical shape:

```json
{
  "error": "User not found",
  "code": "NOT_FOUND",
  "requestId": "abc-123"
}
```

Include a `requestId` (set by a middleware using `crypto.randomUUID()`) so errors can be correlated in logs.

## Summary

| Scenario | Strategy |
|----------|---------|
| Sync throw in route | Express catches automatically |
| Async rejection | Wrap in try/catch + `next(err)`, or use `asyncHandler` |
| Known domain error | Throw `AppError` subclass with status code |
| Unknown bug | Log full stack, return generic 500 |
| Unhandled rejection | `process.on('unhandledRejection')` + exit |
