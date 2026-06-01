# Generics

A generic is a type that takes parameters — a function or type that works on many concrete types while preserving the relationship between them.

## Generic functions

```ts
function first<T>(xs: T[]): T | undefined {
  return xs[0];
}

first([1, 2, 3]);          // T inferred as number, returns number | undefined
first(["a", "b"]);         // T = string
```

The `<T>` is a **type parameter**. The compiler infers it from arguments most of the time.

## Multiple parameters

```ts
function pair<A, B>(a: A, b: B): [A, B] {
  return [a, b];
}

const p = pair(1, "hi");    // [number, string]
```

## Constraints

`extends` restricts what types are allowed:

```ts
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}

longest("hi", "hello");                  // OK, T = string
longest([1], [1, 2, 3]);                 // OK, T = number[]
longest({ length: 1 }, { length: 2 });   // OK
longest(1, 2);                           // Error — number has no length
```

## Default type parameters

```ts
function asMap<K = string, V = unknown>(): Map<K, V> {
  return new Map();
}

asMap();                          // Map<string, unknown>
asMap<number, User>();            // Map<number, User>
```

## Generic interfaces and types

```ts
interface Repository<T> {
  findById(id: string): Promise<T | null>;
  save(item: T): Promise<void>;
}

class UserRepo implements Repository<User> {
  async findById(id: string) { ... }
  async save(u: User) { ... }
}
```

```ts
type Result<T, E = Error> =
  | { ok: true;  value: T }
  | { ok: false; error: E };
```

## Generic classes

```ts
class Box<T> {
  constructor(public value: T) {}
  map<U>(fn: (x: T) => U): Box<U> {
    return new Box(fn(this.value));
  }
}

const b = new Box(10).map(x => `${x}!`);    // Box<string>
```

## keyof and indexed access

```ts
function get<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const u = { name: "Alice", age: 30 };
get(u, "name");          // type string
get(u, "missing");       // Error
```

`keyof T` is the union of T's keys; `T[K]` is the type of the value at key K. These two tools unlock most of the advanced patterns you'll meet.

## A useful pattern: extract a field's type

```ts
type EmailOf<T extends { email: string }> = T["email"];
type Id = User["id"];                          // = number
```

## Generics are erased at compile time

There is no `T` at runtime. You can't write:

```ts
function isT<T>(x: unknown): x is T { ... }   // can't actually check T
```

If you need runtime checking, pass a constructor or a Zod-style schema as an argument.

## Inferring from values

You can capture the type of a literal value:

```ts
function asConst<T>(x: T): T { return x; }
const x = asConst(["red", "green", "blue"] as const);
//    ^? readonly ["red", "green", "blue"]
```

Combined with `as const`, generics let you derive types from data.

## When to reach for generics

- Container/wrapper types (`Result`, `Either`, `Maybe`).
- Higher-order functions that return values related to their inputs.
- APIs where the input type *determines* the output type.

If you're just adding `<T>` to a function to "make it generic" without preserving type relationships, you probably want `unknown` instead.
