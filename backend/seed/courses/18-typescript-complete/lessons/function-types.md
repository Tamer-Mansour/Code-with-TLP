# Function Types in TypeScript

TypeScript models functions as first-class types. Understanding how to annotate and compose function types is essential before you write higher-order utilities or framework glue code.

## Basic function annotations

```ts
// Inline parameter + return type
function add(a: number, b: number): number {
  return a + b;
}

// Arrow function
const multiply = (a: number, b: number): number => a * b;

// Variable with function type annotation
const subtract: (a: number, b: number) => number = (a, b) => a - b;
```

TypeScript infers the return type in most cases, but annotating explicitly makes refactoring safer and the intent clearer.

## Optional and default parameters

```ts
function greet(name: string, greeting?: string): string {
  return `${greeting ?? "Hello"}, ${name}!`;
}

greet("Alice");            // "Hello, Alice!"
greet("Alice", "Hi");      // "Hi, Alice!"
```

Optional parameters (`?`) must come after required ones. Default values work as in JS and the parameter is implicitly optional:

```ts
function repeat(s: string, times: number = 3): string {
  return s.repeat(times);
}
```

## Rest parameters

```ts
function sum(...nums: number[]): number {
  return nums.reduce((acc, n) => acc + n, 0);
}

sum(1, 2, 3, 4);  // 10
```

The rest parameter is always typed as an array.

## Function type aliases

```ts
type Predicate<T> = (value: T) => boolean;
type Transformer<A, B> = (input: A) => B;
type AsyncTask<T> = () => Promise<T>;

const isPositive: Predicate<number> = n => n > 0;
const toString: Transformer<number, string> = n => String(n);
```

Aliases make callback signatures readable and reusable across your codebase.

## Overloads

TypeScript lets you declare multiple signatures for one implementation:

```ts
function format(value: number): string;
function format(value: Date): string;
function format(value: number | Date): string {
  if (value instanceof Date) {
    return value.toISOString();
  }
  return value.toFixed(2);
}

format(3.14159);         // "3.14"
format(new Date());      // ISO string
```

Only the overload signatures are visible to callers — the implementation signature is internal. List more specific overloads first.

## `this` parameter

When writing methods that could be extracted, annotate the implicit `this`:

```ts
interface Counter {
  value: number;
  increment(this: Counter, by?: number): void;
}

const c: Counter = {
  value: 0,
  increment(by = 1) {
    this.value += by;
  },
};
```

If `this` is `void`, TypeScript prevents calling the function with a `this` context:

```ts
function pureLogger(this: void, msg: string): void {
  console.log(msg);
}
```

## `typeof` for capturing function types

```ts
function createUser(name: string, role: "admin" | "user") {
  return { name, role, createdAt: new Date() };
}

type User = ReturnType<typeof createUser>;
// { name: string; role: "admin" | "user"; createdAt: Date }

type CreateUserParams = Parameters<typeof createUser>;
// [name: string, role: "admin" | "user"]
```

`ReturnType<F>` and `Parameters<F>` are built-in utility types that introspect function signatures — handy for deriving types from existing functions without duplicating them.

## Summary table

| Feature | Syntax example |
|---|---|
| Optional param | `fn(x?: string)` |
| Default param | `fn(x = "hi")` |
| Rest param | `fn(...xs: number[])` |
| Type alias | `type F = (x: number) => void` |
| Overload | Multiple `function` signatures before impl |
| Return type | `function fn(): ReturnType` |
| `ReturnType` | `ReturnType<typeof fn>` |
| `Parameters` | `Parameters<typeof fn>` |

Mastering function types unlocks higher-order utilities, proper callback annotations, and the conditional types covered in the next module.
