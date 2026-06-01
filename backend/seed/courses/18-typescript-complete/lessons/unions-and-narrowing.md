# Unions and Narrowing

A **union** type is "this OR that":

```ts
type Id = number | string;

function fmt(id: Id): string {
  return typeof id === "number" ? id.toString() : id.toUpperCase();
}
```

Inside the `if` branch, TypeScript **narrows** `id` to the matching type. You get type-specific methods for free.

## Type guards

The compiler recognizes several narrowing patterns:

```ts
typeof x === "string"
typeof x === "number"
typeof x === "boolean"
x === null
x === undefined
Array.isArray(x)
x instanceof Date
"field" in x
```

```ts
function area(s: { kind: "circle"; r: number } | { kind: "square"; side: number }) {
  if ("r" in s) return Math.PI * s.r ** 2;
  return s.side ** 2;
}
```

## User-defined type guards

```ts
function isString(x: unknown): x is string {
  return typeof x === "string";
}

const v: unknown = "hi";
if (isString(v)) {
  v.toUpperCase();          // OK
}
```

The `x is string` predicate signature tells the compiler "if this returns true, x is a string."

## Assertion functions

```ts
function assertString(x: unknown): asserts x is string {
  if (typeof x !== "string") throw new Error("not a string");
}

assertString(v);
v.toUpperCase();            // OK — TS knows it's a string after assertion
```

Modeled on Node's `assert`. Great for parsing/validation boundaries.

## Optional chaining + nullish coalescing

```ts
const email = user?.profile?.email ?? "n/a";
const fn = user?.fetch?.();
const first = arr?.[0];
```

The `?.` short-circuits if the left side is `null` or `undefined`; `??` provides a default only for `null`/`undefined` (not for `0`, `""`, or `false`).

## Non-null assertion (use sparingly)

```ts
const el = document.getElementById("x")!;
el.click();
```

The `!` says "trust me, this isn't null." A runtime null crashes — and you'll have no compiler help. Prefer narrowing:

```ts
const el = document.getElementById("x");
if (!el) throw new Error("missing");
el.click();
```

## Narrowing by equality

```ts
function f(x: string | number | boolean) {
  if (x === "yes") {
    // x is "yes" here
  } else if (typeof x === "number") {
    // x is number
  } else {
    // x is boolean | string except "yes"
  }
}
```

## The control flow analyzer is smart

```ts
function trim(s: string | null) {
  if (!s) return "";
  return s.trim();          // s narrowed to string
}
```

Reassignments can re-widen:

```ts
let x: string | number = "hello";
x.toUpperCase();           // OK — narrowed to string

x = 5;
x.toUpperCase();           // Error — now narrowed to number
```

## Bottom line

Narrowing is what makes union types ergonomic. Lean on `typeof`, `in`, custom type guards, and `assertX` — they convert "this could be anything" into safe, specific code.
