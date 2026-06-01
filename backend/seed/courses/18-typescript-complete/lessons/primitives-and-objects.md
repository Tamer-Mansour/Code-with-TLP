# Primitives, Arrays, Objects

## Primitive types

```ts
const s: string  = "hello";
const n: number  = 42;
const b: boolean = true;
const u: undefined = undefined;
const nl: null   = null;
const big: bigint = 123n;
const sym: symbol = Symbol("x");
```

## Literal types

```ts
const direction: "left" | "right" | "up" | "down" = "left";
```

The type `"left"` means exactly the string `"left"`. Combined with union, you get a finite enum-like type.

`const` variables get literal types; `let` widens to the parent type:

```ts
const x = 5;     // type 5
let   y = 5;     // type number
```

## Arrays and tuples

```ts
const xs: number[] = [1, 2, 3];
const ys: Array<number> = [1, 2, 3];      // alternate syntax

const pair: [string, number] = ["Alice", 30];     // tuple
const rgb: readonly [number, number, number] = [255, 0, 0];
```

Tuples are fixed-length, position-typed. Useful for "return multiple values."

## Object types

```ts
const user: { id: number; name: string; email?: string } = {
  id: 1, name: "Alice",
};
```

`?` marks the field optional. Use `readonly` to prevent reassignment.

For reuse, give the type a name:

```ts
interface User {
  id: number;
  name: string;
  email?: string;
  readonly createdAt: Date;
}

const u: User = { id: 1, name: "Alice", createdAt: new Date() };
```

## any vs unknown vs never

- **`any`** — opt out of type checking. Use only as a last resort.
- **`unknown`** — "I don't know the type yet." You must narrow before using.
- **`never`** — a value that can never exist (e.g. the return type of `throw`).

```ts
function parse(s: string): unknown {
  return JSON.parse(s);
}

const v = parse("...");
v.toUpperCase();              // Error: v is unknown
if (typeof v === "string") {
  v.toUpperCase();            // OK after narrowing
}
```

Prefer `unknown` over `any`. The compiler forces you to narrow, which is the safe behavior.

## Functions

```ts
function add(a: number, b: number): number {
  return a + b;
}

const sub = (a: number, b: number): number => a - b;

type BinOp = (a: number, b: number) => number;
const mul: BinOp = (a, b) => a * b;
```

Optional and default params:

```ts
function greet(name: string, greeting?: string) {
  return `${greeting ?? "Hello"}, ${name}`;
}
```

Rest params:

```ts
function sum(...xs: number[]): number {
  return xs.reduce((a, b) => a + b, 0);
}
```

## void

`void` is the return type for "I don't return anything useful":

```ts
function log(msg: string): void { console.log(msg); }
```

`void` is *not* `undefined`. A function typed `() => void` can return anything — its return value will simply be ignored. This is intentional and convenient for callbacks.

## Type assertions

When you know more than the compiler:

```ts
const el = document.getElementById("x") as HTMLInputElement;
const v = (something as unknown) as MyType;     // last-resort double cast
```

Assertions don't check at runtime. Use sparingly; prefer narrowing.
