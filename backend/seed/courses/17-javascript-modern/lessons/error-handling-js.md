# Error Handling in JavaScript

Robust JavaScript code anticipates failure. Whether a network request times out, a JSON string is malformed, or a caller passes the wrong type, your code needs a clear strategy for detecting, reporting, and recovering from errors.

## throw and the Error Object

`throw` can throw any value, but throwing an `Error` (or a subclass) is strongly preferred because it captures a stack trace.

```javascript
function divide(a, b) {
  if (b === 0) throw new Error("Division by zero");
  return a / b;
}
```

Built-in error types:

| Type | When it appears |
|------|----------------|
| `Error` | Generic base class |
| `TypeError` | Wrong type (e.g. `null.property`) |
| `RangeError` | Value out of range (e.g. `new Array(-1)`) |
| `SyntaxError` | Bad JSON or eval input |
| `ReferenceError` | Undeclared variable |

## try / catch / finally

```javascript
try {
  const data = JSON.parse(rawInput);
  process(data);
} catch (err) {
  console.error("Parse failed:", err.message);
} finally {
  cleanup();   // always runs — even if catch re-throws
}
```

`finally` is useful for releasing resources (closing files, clearing timers) regardless of success or failure.

## Custom Error Classes

Extend `Error` to give errors a `name` and optional properties:

```javascript
class ValidationError extends Error {
  constructor(field, message) {
    super(message);
    this.name = "ValidationError";
    this.field = field;
  }
}

function validateAge(age) {
  if (typeof age !== "number") throw new ValidationError("age", "Must be a number");
  if (age < 0 || age > 150) throw new ValidationError("age", "Out of range");
}

try {
  validateAge("old");
} catch (err) {
  if (err instanceof ValidationError) {
    console.error(`Field "${err.field}": ${err.message}`);
  } else {
    throw err;   // re-throw unexpected errors
  }
}
```

**Always re-throw** errors you did not expect. Swallowing unknown errors hides bugs.

## Errors in Async Code

With promises, errors flow through `.catch()`:

```javascript
fetch("/api/data")
  .then(r => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  })
  .then(data => render(data))
  .catch(err => console.error("Request failed:", err.message));
```

With `async/await`, use `try/catch` just like synchronous code:

```javascript
async function loadData() {
  try {
    const r = await fetch("/api/data");
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (err) {
    console.error("loadData failed:", err.message);
    return null;   // safe fallback
  }
}
```

## Unhandled Rejections

A promise rejection that no `.catch()` or `try/catch` handles is an **unhandled rejection**. Node.js will terminate the process; browsers log a warning.

```javascript
// In Node.js — catch-all safety net (not a replacement for proper handling)
process.on("unhandledRejection", (reason, promise) => {
  console.error("Unhandled rejection:", reason);
});

// In the browser
window.addEventListener("unhandledrejection", (event) => {
  console.error("Unhandled rejection:", event.reason);
});
```

## Error Handling Checklist

- Throw `Error` instances, not plain strings.
- Use custom error classes for domain errors.
- Re-throw errors you cannot handle.
- Always `await` inside `try` blocks when using `async/await`.
- Add global unhandled-rejection listeners as a last resort, not a first defense.
- Log the full error object (or `err.stack`) — not just `err.message`.

## A Worked Example

```javascript
class AppError extends Error {
  constructor(message, code) {
    super(message);
    this.name = "AppError";
    this.code = code;
  }
}

async function getUser(id) {
  if (!Number.isInteger(id) || id < 1) {
    throw new AppError("Invalid user ID", "INVALID_INPUT");
  }
  const r = await fetch(`/api/users/${id}`);
  if (r.status === 404) throw new AppError("User not found", "NOT_FOUND");
  if (!r.ok) throw new AppError(`Server error ${r.status}`, "SERVER_ERROR");
  return r.json();
}

// caller
try {
  const user = await getUser(userId);
  renderProfile(user);
} catch (err) {
  if (err.code === "NOT_FOUND") showEmptyState();
  else if (err.code === "INVALID_INPUT") showFormError(err.message);
  else throw err;   // unexpected — let it propagate
}
```

Structured errors with codes make it easy for callers to react appropriately without string-matching error messages.
