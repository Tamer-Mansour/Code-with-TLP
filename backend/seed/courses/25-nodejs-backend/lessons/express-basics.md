# Express - Routing and Middleware

Express is the most-used Node web framework. Small surface area, gigantic ecosystem.

## Hello, Express

```bash
npm init -y
npm install express
```

```js
import express from "express";

const app = express();
app.use(express.json());      // parse JSON bodies

app.get("/", (req, res) => res.send("hello"));
app.get("/users/:id", (req, res) => {
  res.json({ id: req.params.id });
});

app.listen(3000);
```

## Route parameters and query strings

```js
app.get("/users/:id/posts/:postId", (req, res) => {
  const { id, postId } = req.params;
  const { sort = "asc" } = req.query;
  res.json({ id, postId, sort });
});
```

`req.params` from URL placeholders, `req.query` from `?key=value`.

## Middleware

A middleware is `function (req, res, next)`. Use it for cross-cutting concerns:

```js
app.use((req, res, next) => {
  console.log(req.method, req.url);
  next();
});

app.use("/api", apiRouter);   // mount a sub-router under /api
```

Common middleware:

```js
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";

app.use(helmet());            // security headers
app.use(cors({ origin: "..." }));
app.use(express.json({ limit: "1mb" }));
app.use(morgan("combined"));  // request logging
```

## Error handling

Errors thrown in async handlers must be `next(err)`'d (Express 4) or just `throw`n in Express 5:

```js
app.get("/users/:id", async (req, res, next) => {
  try {
    const u = await db.findUser(req.params.id);
    if (!u) return res.status(404).json({ error: "not found" });
    res.json(u);
  } catch (e) {
    next(e);
  }
});

// error-handling middleware (4 args)
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: "server error" });
});
```

## Routers — split big apps

```js
// routes/users.js
import { Router } from "express";
const router = Router();

router.get("/", listUsers);
router.get("/:id", getUser);
router.post("/", createUser);

export default router;

// app.js
import users from "./routes/users.js";
app.use("/api/users", users);
```

## Validation

Use **Zod** (modern, type-safe) or **Joi**:

```js
import { z } from "zod";

const CreateUser = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  age: z.number().int().min(0),
});

app.post("/users", (req, res) => {
  const parsed = CreateUser.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ errors: parsed.error.flatten() });
  }
  const user = await db.create(parsed.data);
  res.status(201).json(user);
});
```

## Alternatives to Express

- **Fastify** — faster, built-in schema validation, modern.
- **Hono** — runs on Node, Bun, Deno, Edge runtimes.
- **NestJS** — opinionated, Angular-flavored, DI heavy.

For new projects in 2025, **Fastify** is the modern default for performance-sensitive APIs. Express remains the safe choice for ecosystem compatibility.

## Don't forget

- Always set a timeout for upstream calls.
- Always validate input.
- Never trust `req.body` shape — it's whatever the client sent.
- Log structured (`pino`), not `console.log`.
