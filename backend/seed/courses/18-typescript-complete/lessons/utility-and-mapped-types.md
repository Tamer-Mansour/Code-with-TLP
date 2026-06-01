# Utility Types and Mapped Types

TypeScript ships a handful of built-in **utility types** that transform other types. Knowing them by heart saves dozens of lines of bespoke code.

## The essentials

```ts
interface User {
  id: number;
  name: string;
  email: string;
  password: string;
}

type PublicUser = Omit<User, "password">;       // everything except password
type Credentials = Pick<User, "email" | "password">;
type PartialUser = Partial<User>;               // all fields optional
type RequiredUser = Required<User>;             // all fields required (drops `?`)
type ReadonlyUser = Readonly<User>;             // all fields readonly
```

## Record

```ts
type UserMap = Record<string, User>;            // { [key: string]: User }
type RolePermissions = Record<"admin" | "user", string[]>;
//   ^? { admin: string[]; user: string[] }
```

## Extract and Exclude

```ts
type Animals = "dog" | "cat" | "bird";
type Mammals = Extract<Animals, "dog" | "cat">;     // "dog" | "cat"
type NonMammals = Exclude<Animals, "dog" | "cat">;  // "bird"
```

## NonNullable

```ts
type Maybe = string | number | null | undefined;
type Definite = NonNullable<Maybe>;     // string | number
```

## ReturnType and Parameters

```ts
function greet(name: string): string { return `hi, ${name}`; }

type R = ReturnType<typeof greet>;          // string
type P = Parameters<typeof greet>;          // [name: string]
```

Especially useful when working with library functions whose return shape you don't have a name for.

## Awaited

```ts
async function fetchUser(): Promise<User> { ... }
type U = Awaited<ReturnType<typeof fetchUser>>;     // User
```

Unwraps any number of nested `Promise<...>`.

## Writing your own — mapped types

```ts
type Nullable<T> = { [K in keyof T]: T[K] | null };

type NullableUser = Nullable<User>;
// { id: number | null; name: string | null; ... }
```

Iterate over the keys of `T` with `[K in keyof T]` and rewrite each property.

Modifiers `+`/`-` add or remove `readonly`/`?`:

```ts
type Writable<T> = { -readonly [K in keyof T]: T[K] };
type DeepRequired<T> = { [K in keyof T]-?: T[K] };
```

## Template literal types

You can manipulate strings at the type level:

```ts
type Hello<T extends string> = `hello, ${T}`;
type Greeting = Hello<"world">;     // "hello, world"

type EventName<T extends string> = `on${Capitalize<T>}`;
type Click = EventName<"click">;    // "onClick"
```

Combined with `keyof`, this lets you define rich, typed event APIs.

## Conditional types

```ts
type IsString<T> = T extends string ? true : false;
type A = IsString<"hi">;     // true
type B = IsString<5>;        // false
```

The `extends ? :` works on types. Combined with `infer`, you can extract pieces:

```ts
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
type FirstArg<T> = T extends (first: infer A, ...rest: any[]) => any ? A : never;
```

`infer R` introduces a new type variable that captures whatever matches that slot.

## A real-world combo

```ts
// Make everything in T nullable AND optional, recursively.
type DeepNullablePartial<T> = T extends object
  ? { [K in keyof T]?: DeepNullablePartial<T[K]> | null }
  : T;
```

## When NOT to over-engineer

A function that takes a `User` and returns `Omit<User, "password">` is fine. A 50-line conditional type that recursively transforms 5 nested generics is a maintenance nightmare. **If your colleagues can't read it, simplify.**
