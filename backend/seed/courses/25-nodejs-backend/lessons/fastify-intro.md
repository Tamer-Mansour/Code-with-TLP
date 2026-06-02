# Introduction to Fastify

Fastify is a high-performance, production-ready Node.js web framework. It is consistently 2-3x faster than Express on raw throughput benchmarks, has built-in JSON schema validation, and ships with first-class TypeScript support.

## Why Consider Fastify?

| | Express | Fastify |
|-|---------|---------|
| Requests/sec (hello world) | ~30,000 | ~75,000 |
| Built-in schema validation | No | Yes (ajv) |
| TypeScript types | Community | First-class |
| Plugin system | Middleware | Encapsulated plugins |
| JSON serialisation | Manual | Auto via schema |
| Async support | Manual wrapping | Native |

## Getting Started

```bash
npm install fastify
```

```js
// server.js
import Fastify from "fastify";

const fastify = Fastify({ logger: true });   // built-in pino logger

fastify.get("/", async (request, reply) => {
  return { hello: "world" };                 // return value is auto-serialised
});

await fastify.listen({ port: 3000, host: "0.0.0.0" });
```

`return`ing an object from a Fastify handler serialises it to JSON automatically — no `res.json()` needed.

## Route Schema — Validation + Serialisation

```js
const createUserSchema = {
  body: {
    type: "object",
    required: ["name", "email"],
    properties: {
      name:  { type: "string", minLength: 1, maxLength: 100 },
      email: { type: "string", format: "email" },
      age:   { type: "integer", minimum: 0 },
    },
    additionalProperties: false,
  },
  response: {
    201: {
      type: "object",
      properties: {
        id:    { type: "integer" },
        name:  { type: "string" },
        email: { type: "string" },
      },
    },
  },
};

fastify.post("/users", { schema: createUserSchema }, async (request, reply) => {
  const user = await db.createUser(request.body);  // body is already validated
  reply.code(201);
  return user;  // serialised against response schema — extra fields stripped
});
```

The `response` schema serves dual purposes: it strips extra fields (security) and makes serialisation faster by skipping dynamic type-checking.

## Plugins — Fastify's Composition Model

Fastify uses encapsulated plugins to avoid the global-middleware problem Express has:

```js
// plugins/database.js
import fp from "fastify-plugin";   // fp breaks encapsulation so the decoration is global
import pg from "pg";

async function database(fastify, opts) {
  const pool = new pg.Pool({ connectionString: opts.connectionString });
  fastify.decorate("db", pool);    // available as fastify.db everywhere
  fastify.addHook("onClose", () => pool.end());
}

export default fp(database);

// app.js
await fastify.register(database, { connectionString: process.env.DATABASE_URL });
await fastify.register(import("./routes/users.js"), { prefix: "/api/users" });
```

## Hooks

```js
fastify.addHook("onRequest", async (request, reply) => {
  request.requestId = crypto.randomUUID();
});

fastify.addHook("onResponse", async (request, reply) => {
  fastify.log.info({ requestId: request.requestId, ms: reply.elapsedTime }, "request complete");
});
```

Hooks replace Express middleware. They are typed, async-native, and scoped to the plugin context.

## When to Choose Fastify Over Express

- High-throughput APIs (Fastify's speed advantage matters above ~5,000 req/s).
- TypeScript projects — Fastify's types are excellent.
- New projects without an existing Express codebase.
- When you want schema-driven validation baked in.

Express remains the safer choice when you depend on Express-specific middleware that has no Fastify equivalent, or when your team is not ready to learn Fastify's plugin model.
