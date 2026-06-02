# Conditional Types

Conditional types let you express type-level logic with an `if/else` syntax. They are the mechanism behind most of TypeScript's built-in utility types and many library types.

## Basic syntax

```ts
type IsString<T> = T extends string ? "yes" : "no";

type A = IsString<string>;      // "yes"
type B = IsString<number>;      // "no"
type C = IsString<"hello">;     // "yes"  (string literal extends string)
```

Read it as: *"If `T` is assignable to `string`, the result is `"yes"`, otherwise `"no"`."*

## Conditional types distribute over unions

When `T` is a naked type parameter and you pass a union, the conditional type is applied to **each member** of the union separately — this is called *distributive* behavior:

```ts
type Flatten<T> = T extends Array<infer Item> ? Item : T;

type A = Flatten<string[]>;           // string
type B = Flatten<number[]>;           // number
type C = Flatten<string | number[]>;  // string | number
```

`string | number[]` becomes `Flatten<string> | Flatten<number[]>` = `string | number`.

To suppress distribution, wrap `T` in a tuple:

```ts
type NonDistributed<T> = [T] extends [string] ? "yes" : "no";

type D = NonDistributed<string | number>;  // "no" (not "yes | no")
```

## `infer` — extracting types inside a conditional

`infer` lets you capture a part of the matched type into a type variable:

```ts
// Extract the return type of a function
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

type R1 = ReturnType<() => string>;             // string
type R2 = ReturnType<(x: number) => boolean>;   // boolean

// Extract the element type of an array
type ElementType<T> = T extends (infer E)[] ? E : never;

type E1 = ElementType<Date[]>;   // Date
type E2 = ElementType<string>;   // never
```

`infer` only works inside a conditional type's `extends` clause.

## Chaining conditions

```ts
type TypeName<T> =
  T extends string  ? "string"  :
  T extends number  ? "number"  :
  T extends boolean ? "boolean" :
  T extends null    ? "null"    :
  T extends undefined ? "undefined" :
  "object";

type T1 = TypeName<true>;     // "boolean"
type T2 = TypeName<() => void>;  // "object"
```

## Built-in conditional utility types

| Utility | Definition (simplified) |
|---|---|
| `ReturnType<F>` | `F extends (...args: any[]) => infer R ? R : never` |
| `Parameters<F>` | `F extends (...args: infer P) => any ? P : never` |
| `Awaited<T>` | Recursively unwraps `Promise<T>` |
| `InstanceType<C>` | `C extends new (...args: any[]) => infer I ? I : never` |
| `NonNullable<T>` | `T extends null \| undefined ? never : T` |

## Practical example: `PickByValue`

```ts
// Keep only keys whose value type extends V
type PickByValue<T, V> = {
  [K in keyof T as T[K] extends V ? K : never]: T[K];
};

interface Config {
  host: string;
  port: number;
  debug: boolean;
  timeout: number;
}

type NumberFields = PickByValue<Config, number>;
// { port: number; timeout: number }
```

This combines a mapped type with a conditional type in the `as` remapping clause — a very common advanced pattern.

## When to use conditional types

- Writing utility types that operate on function, array, or Promise types.
- Filtering union members or object keys by type.
- Library types where the output type depends on the input type in a complex way.

Avoid conditional types for simple transformations — mapped types or intersections are cleaner. Reach for conditional types when you genuinely need type-level branching.
