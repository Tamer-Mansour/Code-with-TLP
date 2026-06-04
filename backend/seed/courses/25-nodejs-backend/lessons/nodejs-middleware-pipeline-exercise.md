# Middleware Pipeline Executor

Express.js processes every request through a pipeline of middleware functions. Understanding how this pipeline behaves — including normal flow, early termination, and error propagation — is fundamental to building reliable APIs.

## The Middleware Contract

Every Express middleware function receives `(req, res, next)` and must do exactly one of:

1. **Call `next()`** — pass control to the next middleware
2. **Send a response** — terminate the chain with `res.send()`, `res.json()`, etc.
3. **Call `next(err)`** — pass an error down to the nearest error-handling middleware

```js
// Normal middleware
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next(); // pass control onward
});

// Early termination
app.use((req, res, next) => {
  if (!req.headers.authorization) {
    return res.status(401).json({ error: "Unauthorized" }); // stops here
  }
  next();
});

// Error propagation
app.use(async (req, res, next) => {
  try {
    const user = await db.findUser(req.userId);
    req.user = user;
    next();
  } catch (err) {
    next(err); // jumps to error handler
  }
});
```

## Error-Handling Middleware

Error handlers have a **four-argument signature** `(err, req, res, next)`. When `next(err)` is called, Express skips all regular middleware until it finds an error handler:

```js
// Regular middleware are skipped when an error is active
app.use((req, res, next) => {
  // This is SKIPPED if an error was passed to next(err)
  next();
});

// Error handler catches it
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: "Something went wrong" });
});
```

## Practical Pipeline Example

```js
import express from "express";
import helmet from "helmet";
import cors from "cors";
import morgan from "morgan";

const app = express();

// 1. Security headers
app.use(helmet());

// 2. CORS
app.use(cors({ origin: process.env.ALLOWED_ORIGIN }));

// 3. Request logging
app.use(morgan("combined"));

// 4. Body parsing
app.use(express.json({ limit: "1mb" }));

// 5. Routes
app.use("/api/users", usersRouter);

// 6. 404 handler (no route matched)
app.use((req, res) => {
  res.status(404).json({ error: "Not Found" });
});

// 7. Error handler (must be last)
app.use((err, req, res, next) => {
  res.status(err.status ?? 500).json({ error: err.message });
});
```

## Common Mistake: Forgetting `return`

```js
app.use((req, res, next) => {
  if (!req.user) {
    res.status(401).json({ error: "Unauthorized" });
    // BUG: next() still called below — headers already sent!
  }
  next();
});

// Correct:
app.use((req, res, next) => {
  if (!req.user) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  next();
});
```

## Further Reading

- **"Practical Node.js" by Azat Mardan** — https://github.com/azat-co/practicalnode — Chapter 4 covers Express.js 4 middleware in depth with real-world patterns for authentication, logging, and error handling.
- **"Backend Development Textbook" by Brigitte Jellinek** — https://backend-development.github.io/ — covers Express web applications including the middleware pipeline with university-level clarity.

## Exercise

In this exercise you will simulate a middleware pipeline. Given a sequence of middleware behaviors, trace which labels get logged and what the final response is.
