# Async TypeScript

TypeScript tracks types through `Promise` chains and `async`/`await` the same way it tracks synchronous types — so you get full autocompletion and error checking on async values.

## Typing async functions

An `async` function always returns a `Promise`. TypeScript infers the inner type:

```ts
async function fetchName(): Promise<string> {
  return "Alice";            // TypeScript checks this matches Promise<string>
}

const name = await fetchName();   // type: string
```

If you return `"Alice"` but annotate `Promise<number>`, the compiler errors — exactly what you want.

## `Awaited<T>` utility type

`Awaited<T>` recursively unwraps a `Promise`:

```ts
type A = Awaited<Promise<string>>;              // string
type B = Awaited<Promise<Promise<number>>>;     // number
type C = Awaited<string>;                       // string (no-op on non-Promise)
```

This is useful when extracting the result type from an async function:

```ts
async function loadUser() {
  return { id: 1, name: "Alice" };
}

type User = Awaited<ReturnType<typeof loadUser>>;
// { id: number; name: string }
```

## Error handling with typed errors

`catch` clauses give `error: unknown` by default (with `useUnknownInCatchVariables`, the safe default in strict mode). Always narrow before using:

```ts
async function safeFetch(url: string): Promise<string> {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.text();
  } catch (err) {
    if (err instanceof Error) {
      console.error(err.message);
    }
    throw err;
  }
}
```

## Typed Result pattern

Rather than throwing, many TypeScript codebases wrap async results in a discriminated union:

```ts
type AsyncResult<T> =
  | { ok: true;  data: T }
  | { ok: false; error: string };

async function getUser(id: number): Promise<AsyncResult<User>> {
  try {
    const user = await db.users.findById(id);
    if (!user) return { ok: false, error: "Not found" };
    return { ok: true, data: user };
  } catch {
    return { ok: false, error: "Database error" };
  }
}

const result = await getUser(42);
if (result.ok) {
  console.log(result.data.name);  // narrowed to User
} else {
  console.error(result.error);
}
```

## `Promise.all` and `Promise.allSettled`

TypeScript infers tuple types for `Promise.all`:

```ts
const [user, posts] = await Promise.all([
  fetchUser(1),     // Promise<User>
  fetchPosts(1),    // Promise<Post[]>
]);
// user: User, posts: Post[]
```

With `Promise.allSettled`, each result is `PromiseSettledResult<T>`:

```ts
const results = await Promise.allSettled([fetchUser(1), fetchUser(99)]);

for (const r of results) {
  if (r.status === "fulfilled") {
    console.log(r.value.name);   // User
  } else {
    console.error(r.reason);
  }
}
```

## Async iterators

Async generators yield values lazily over time:

```ts
async function* streamLines(url: string): AsyncGenerator<string> {
  const res = await fetch(url);
  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value);
    const lines = buffer.split("\n");
    buffer = lines.pop()!;
    for (const line of lines) yield line;
  }
}

for await (const line of streamLines("/api/stream")) {
  console.log(line);
}
```

## Summary

| Pattern | Type outcome |
|---|---|
| `async function fn(): Promise<T>` | Return type enforced |
| `await promise` | Unwraps `Promise<T>` to `T` |
| `Awaited<ReturnType<F>>` | Extracts inner type of async fn |
| `Promise.all([p1, p2])` | Tuple `[T1, T2]` |
| `catch (err)` | `err: unknown` — must narrow |
| Discriminated union result | Explicit error path without `throw` |

Async TypeScript is idiomatic when you combine `async`/`await`, typed result discriminated unions, and `Awaited` to derive types — you get type safety through the entire async call chain.
