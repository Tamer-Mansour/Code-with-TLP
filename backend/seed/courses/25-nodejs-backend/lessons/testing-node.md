# Testing Node.js APIs

Untested APIs accumulate hidden bugs and make refactoring dangerous. This lesson covers the testing pyramid for Node backends: unit tests, integration tests, and the built-in Node test runner.

## Testing Pyramid

```
        /\
       /E2E\        — few, slow, full stack
      /------\
     / Integr \     — moderate, test DB + HTTP layer
    /----------\
   /  Unit Tests \  — many, fast, pure functions
  /--------------\
```

Focus most effort on unit tests (fast, reliable, no I/O). Add integration tests for the HTTP + DB layer. Add E2E tests sparingly for critical user flows.

## Node's Built-in Test Runner (Node 18+)

No external dependency needed:

```js
// src/lib/calc.test.js
import { test, describe, before, after } from "node:test";
import assert from "node:assert/strict";
import { add, divide } from "./calc.js";

describe("Math utils", () => {
  test("add returns sum", () => {
    assert.equal(add(2, 3), 5);
  });

  test("divide by zero throws", () => {
    assert.throws(() => divide(1, 0), /Cannot divide by zero/);
  });
});
```

```bash
# Run all .test.js files
node --test src/**/*.test.js
```

## Testing Service Logic (Unit)

Isolate business logic from I/O by using dependency injection:

```js
// services/userService.js
export function createUserService({ db, mailer }) {
  return {
    async createUser(data) {
      const existing = await db.findByEmail(data.email);
      if (existing) throw new Error("Email already in use");
      const user = await db.insert(data);
      await mailer.sendWelcome(user.email);
      return user;
    },
  };
}

// services/userService.test.js
import { test } from "node:test";
import assert from "node:assert/strict";
import { createUserService } from "./userService.js";

test("createUser throws when email taken", async () => {
  const db = { findByEmail: async () => ({ id: 1 }), insert: async () => {} };
  const mailer = { sendWelcome: async () => {} };
  const service = createUserService({ db, mailer });

  await assert.rejects(
    () => service.createUser({ email: "taken@x.com" }),
    /Email already in use/
  );
});
```

Dependency injection makes code both testable and flexible.

## Integration Testing with Supertest

Test the full HTTP layer (routing, middleware, validation, error handling) without spinning up a real server:

```bash
npm install -D supertest
```

```js
// tests/users.test.js
import { test } from "node:test";
import assert from "node:assert/strict";
import request from "supertest";
import { buildApp } from "../src/app.js";

// app.js exports the Express app WITHOUT calling app.listen()
const app = buildApp({ db: mockDb });

test("POST /users returns 201 with valid body", async () => {
  const res = await request(app)
    .post("/users")
    .send({ name: "Alice", email: "alice@example.com" });

  assert.equal(res.status, 201);
  assert.equal(res.body.email, "alice@example.com");
});

test("POST /users returns 400 with invalid email", async () => {
  const res = await request(app)
    .post("/users")
    .send({ name: "Bob", email: "not-an-email" });

  assert.equal(res.status, 400);
  assert.ok(res.body.details?.email);
});
```

## Test Coverage

```bash
node --test --experimental-test-coverage src/**/*.test.js
```

Coverage is a useful sanity check, not a goal. 100% coverage with weak assertions is worse than 70% coverage with strong assertions.

## Vitest — Modern Alternative

If you prefer a Jest-compatible API with faster execution:

```bash
npm install -D vitest
```

```js
import { describe, it, expect } from "vitest";

describe("add", () => {
  it("returns sum", () => {
    expect(add(1, 2)).toBe(3);
  });
});
```

Run with `npx vitest`. Works with ESM out of the box.

## Test Organisation Best Practices

- Keep test files next to source files (`calc.js` + `calc.test.js`) for unit tests.
- Keep integration/E2E tests in a separate `tests/` directory.
- Each test should set up its own state and not depend on other tests.
- Use `before` / `after` hooks to open and close DB connections in integration tests.
- Use in-memory or test-specific databases — never run tests against production.

## Summary

| Test type | Tool | What it tests |
|-----------|------|---------------|
| Unit | Node built-in / Vitest | Pure functions, services |
| Integration | Supertest + built-in | HTTP routes + middleware |
| E2E | Playwright / Cypress | Full user flows in browser |
