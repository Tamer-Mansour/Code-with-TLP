# Fetch, Promises, and async/await

Modern web pages talk to backends (like your Spring REST APIs) over HTTP without reloading the page. In the browser, the standard way to do this is the **Fetch API**, which is built on **Promises**. The `async/await` keywords then let you write that asynchronous code as if it were synchronous and readable.

## Why asynchronous?

A network request takes time. JavaScript runs on a single thread, so it must **not** block while waiting for a response. Instead, an HTTP call returns a `Promise`: a placeholder for a value that will arrive *later* (resolved) or fail (rejected).

A `Promise` has three states:

| State | Meaning |
|-----------|---------------------------------------------|
| pending | The operation is still in progress |
| fulfilled | It completed successfully (has a value) |
| rejected | It failed (has an error) |

## Fetch with `.then()`

`fetch(url)` returns a Promise that resolves to a `Response` object. You then call `.json()` (which itself returns a Promise) to parse the body.

```javascript
fetch("http://localhost:8080/api/courses")
  .then((response) => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  })
  .then((courses) => console.log(courses))
  .catch((error) => console.error("Request failed:", error));
```

## The cleaner way: `async/await`

`await` pauses inside an `async` function until the Promise settles, returning its resolved value. Wrap calls in `try/catch` to handle errors like normal exceptions.

```javascript
async function loadCourses() {
  try {
    const response = await fetch("http://localhost:8080/api/courses");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const courses = await response.json();
    return courses;
  } catch (error) {
    console.error("Request failed:", error);
    return [];
  }
}

loadCourses().then((courses) => console.log(courses));
```

### Sending data (POST)

To create a resource via your Spring API, pass an options object with the method, headers, and a JSON-encoded body.

```javascript
async function createCourse(course) {
  const response = await fetch("http://localhost:8080/api/courses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(course),
  });
  if (!response.ok) {
    throw new Error(`Create failed: HTTP ${response.status}`);
  }
  return response.json();
}

createCourse({ title: "Spring Basics", level: "Beginner" })
  .then((saved) => console.log("Created:", saved));
```

## Running calls in parallel

When requests do not depend on each other, fire them together with `Promise.all` instead of awaiting one after another.

```javascript
const [courses, students] = await Promise.all([
  fetch("/api/courses").then((r) => r.json()),
  fetch("/api/students").then((r) => r.json()),
]);
```

## Common mistakes and best practices

- **`fetch` does not reject on HTTP errors.** A `404` or `500` still *resolves*. Always check `response.ok` (true for status 200–299) and throw manually.
- **Forgetting `await` on `.json()`** — it also returns a Promise, so `const data = response.json()` gives you a Promise, not the data.
- **`await` only works inside `async` functions** (or at the top level of an ES module).
- **Always handle errors** with `try/catch` (or `.catch`) so a failed network call does not crash silently.
- **Don't serialize parallel work** — use `Promise.all` when calls are independent.

## Summary

`fetch` returns Promises that represent future HTTP results; `async/await` lets you consume them in clear, linear code. Remember to check `response.ok`, `await` the `.json()` parse, and wrap everything in `try/catch`.
