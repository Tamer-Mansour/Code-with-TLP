# Promises and async/await

## Promise basics

A `Promise` is "a value, eventually." It has three states:

- **pending** — not done yet.
- **fulfilled** — succeeded with a value.
- **rejected** — failed with an error.

```javascript
const p = new Promise((resolve, reject) => {
  setTimeout(() => resolve("done"), 1000);
});

p.then(v => console.log(v));       // "done" (after 1s)
p.catch(err => console.error(err));
p.finally(() => console.log("settled"));
```

You rarely call `new Promise` — most APIs return promises directly (`fetch`, `fs.promises`, anything `async`).

## Chaining

```javascript
fetch("/api/users")
  .then(r => r.json())
  .then(users => render(users))
  .catch(err => alert(err.message));
```

Each `.then` returns a new promise. Throw inside a `.then` and `.catch` handles it.

## async / await — the modern face

```javascript
async function loadUsers() {
  try {
    const r = await fetch("/api/users");
    const users = await r.json();
    return render(users);
  } catch (err) {
    alert(err.message);
  }
}
```

`async` functions always return a promise. `await` pauses the function until the awaited promise settles, then resumes with the value (or throws the rejection).

You can only `await` inside an `async` function — or at top-level in ES modules.

## Parallel with Promise.all

```javascript
const [a, b, c] = await Promise.all([
  fetchA(),
  fetchB(),
  fetchC(),
]);
```

All three fly in parallel; the `await` resolves when **all** have. If *any* rejects, the whole `Promise.all` rejects with that error and abandons the rest.

For "succeed if any succeeds":

```javascript
await Promise.any([f1, f2, f3]);   // first fulfillment
```

For "wait for all settlements, no short-circuit":

```javascript
const results = await Promise.allSettled([f1, f2, f3]);
// each result: { status: "fulfilled", value } or { status: "rejected", reason }
```

## Common traps

### Sequential when you meant parallel

```javascript
for (const id of ids) {
  const u = await fetchUser(id);    // serial — slow
  ...
}

// fix:
const users = await Promise.all(ids.map(id => fetchUser(id)));
```

### Forgotten await

```javascript
async function save() {
  const r = fetch("/api/save", { method: "POST" });  // never awaited!
  return "ok";    // returns before fetch finished, errors swallowed
}
```

Linters catch this — `eslint-plugin-promise`, `no-floating-promises`.

### try/catch around the wrong line

```javascript
async function f() {
  try {
    const p = fetch(...);            // not awaited - errors won't be caught!
  } catch (e) { ... }
}
```

Always `await` inside the try block.

## Timeouts

`Promise.race` lets you race a value against a timer:

```javascript
function withTimeout(p, ms) {
  return Promise.race([
    p,
    new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), ms)),
  ]);
}
```

Modern alternative — AbortController on `fetch`:

```javascript
const ac = new AbortController();
setTimeout(() => ac.abort(), 3000);
await fetch(url, { signal: ac.signal });
```

## A useful mental model

`async` makes a function return a promise; `await` unwraps a promise. Everything else is sugar over the same chained `.then` machinery.
