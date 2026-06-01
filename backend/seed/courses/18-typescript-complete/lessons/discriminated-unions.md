# Discriminated Unions and Exhaustiveness

A **discriminated union** is a union of object types that all share a common literal field — the *discriminant*. They're TypeScript's most powerful modelling pattern.

## The shape

```ts
type Shape =
  | { kind: "circle";    radius: number }
  | { kind: "square";    side:   number }
  | { kind: "rectangle"; width:  number; height: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle":    return Math.PI * s.radius ** 2;
    case "square":    return s.side ** 2;
    case "rectangle": return s.width * s.height;
  }
}
```

Inside each `case`, TypeScript narrows `s` to the matching variant — you get exactly the fields that variant defines. No type assertions, no defensive `as any`.

## Why "discriminated"

The `kind` field — the discriminant — distinguishes the variants. It's usually a string literal, but can be a number or boolean. Pick whatever's natural to your domain.

Common alternatives: `type`, `tag`, `_type`, `__typename` (GraphQL convention).

## Exhaustiveness checking

You want the compiler to complain if you add a new variant and forget a case. Use the `never` trick:

```ts
function area(s: Shape): number {
  switch (s.kind) {
    case "circle":    return Math.PI * s.radius ** 2;
    case "square":    return s.side ** 2;
    case "rectangle": return s.width * s.height;
    default:
      const _exhaustive: never = s;
      throw new Error(`unhandled: ${(s as any).kind}`);
  }
}
```

If you add `triangle` to `Shape` and don't add a case, `_exhaustive: never = s` errors — `s` would no longer be `never`.

The same idiom in an arrow + helper:

```ts
function assertNever(x: never): never {
  throw new Error(`unhandled: ${JSON.stringify(x)}`);
}

switch (s.kind) {
  case "circle":    ...
  case "square":    ...
  case "rectangle": ...
  default: assertNever(s);
}
```

## Modelling state with discriminated unions

State machines, API responses, and parser nodes all want this:

```ts
type Request<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error";   error: Error };

function render(r: Request<User[]>) {
  switch (r.status) {
    case "idle":    return null;
    case "loading": return <Spinner />;
    case "success": return <UserList users={r.data} />;
    case "error":   return <Alert message={r.error.message} />;
  }
}
```

`r.data` is only available in `success`; `r.error` only in `error`. You can't accidentally read missing fields.

## API responses

```ts
type ApiResult<T> =
  | { ok: true;  data: T }
  | { ok: false; error: string };

async function fetchUsers(): Promise<ApiResult<User[]>> {
  try {
    const r = await fetch("/api/users");
    if (!r.ok) return { ok: false, error: `${r.status}` };
    return { ok: true, data: await r.json() };
  } catch (e) {
    return { ok: false, error: String(e) };
  }
}

const r = await fetchUsers();
if (r.ok) {
  console.log(r.data.length);     // narrowed to T
} else {
  console.log(r.error);            // narrowed to string
}
```

## When NOT to use

If all variants share most fields, you might prefer a plain interface with optional fields. The discriminated union shines when each variant has *meaningfully different* data.

## Bottom line

Whenever you see code with optional fields that go together ("if status is success, data is set"), you have a discriminated union waiting to be modelled. Reach for them; the compiler-enforced exhaustiveness is a permanent gift.
