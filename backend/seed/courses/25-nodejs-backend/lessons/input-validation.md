# Input Validation with Zod

Never trust data that arrives from the network. Input validation is the first line of defense: reject malformed requests early, return helpful errors to clients, and keep business logic clean.

## Why Zod?

**Zod** is the modern standard for TypeScript/JavaScript validation. Unlike Joi (which predates TypeScript) or manual `if` checks, Zod schemas double as TypeScript types — one source of truth.

```bash
npm install zod
```

## Defining Schemas

```js
import { z } from "zod";

const CreateUserSchema = z.object({
  name:  z.string().min(1, "Name is required").max(100),
  email: z.string().email("Invalid email"),
  age:   z.number().int().min(0).max(150).optional(),
  role:  z.enum(["admin", "user", "guest"]).default("user"),
});

// Infer the TypeScript type (in a .ts project)
// type CreateUser = z.infer<typeof CreateUserSchema>;
```

## Parsing vs Safe-Parsing

```js
// parse — throws ZodError on failure
const data = CreateUserSchema.parse(req.body);

// safeParse — returns { success, data } | { success, error }
const result = CreateUserSchema.safeParse(req.body);
if (!result.success) {
  return res.status(400).json({ errors: result.error.flatten().fieldErrors });
}
const user = result.data;  // fully typed, guaranteed valid
```

Prefer `safeParse` in HTTP handlers — it lets you control the response format instead of relying on a thrown error reaching your error middleware.

## Validation Middleware

Extract validation into reusable middleware to keep route handlers clean:

```js
// middleware/validate.js
import { z } from "zod";

export function validate(schema) {
  return (req, res, next) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({
        error: "Validation failed",
        details: result.error.flatten().fieldErrors,
      });
    }
    req.validated = result.data;   // attach validated data
    next();
  };
}

// routes/users.js
import { validate } from "../middleware/validate.js";

router.post("/", validate(CreateUserSchema), async (req, res) => {
  const user = await userService.create(req.validated);
  res.status(201).json(user);
});
```

## Common Validators

| Use case | Zod method |
|----------|-----------|
| Non-empty string | `z.string().min(1)` |
| Email | `z.string().email()` |
| URL | `z.string().url()` |
| UUID | `z.string().uuid()` |
| Positive integer | `z.number().int().positive()` |
| Date string | `z.coerce.date()` |
| Nullable field | `z.string().nullable()` |
| Optional field | `z.string().optional()` |
| Array | `z.array(z.string()).min(1)` |

## Validating Query Params and Route Params

Route params and query strings are always strings — use `z.coerce` to convert:

```js
const GetUsersQuery = z.object({
  page:  z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  sort:  z.enum(["asc", "desc"]).default("asc"),
});

app.get("/users", (req, res) => {
  const query = GetUsersQuery.parse(req.query);
  // query.page is a number, not a string
});
```

## Error Response Format

Adopt a consistent error shape across your API:

```json
{
  "error": "Validation failed",
  "details": {
    "email": ["Invalid email"],
    "name":  ["String must contain at least 1 character"]
  }
}
```

Clients can display field-level errors without parsing a generic error message. Document this shape in your API docs.

## Zod vs Alternatives

| Library | Strengths | When to choose |
|---------|-----------|----------------|
| **Zod** | TypeScript-first, composable | New Node/TS projects |
| **Joi** | Mature, large ecosystem | Legacy projects |
| **Yup** | Similar to Joi, lighter | React form validation |
| **class-validator** | Decorator-based | NestJS |

For Node projects started in 2024+, Zod is the clear default.
